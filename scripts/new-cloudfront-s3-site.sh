#!/usr/bin/env bash
# scripts/new-cloudfront-s3-site.sh
# ─────────────────────────────────────────────────────────────────────────────
# ClawWorks Standard: Create a new static site on AWS S3 + CloudFront
#
# Bakes in:
#   - HTTPS-only with ACM certificate
#   - CloudFront Function: directory index URL rewrite (/path → /path/index.html)
#   - Compression enabled
#   - Custom error handling (403/404 → 200 index.html for client-side routing)
#   - TLSv1.2_2021 minimum
#   - PriceClass_100 (US + Europe)
#
# Usage:
#   ./scripts/new-cloudfront-s3-site.sh \
#     --domain example.com \
#     --bucket example.com \
#     --cert-arn arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID \
#     [--region us-east-1] \
#     [--include-www]
#
# Prerequisites:
#   - AWS CLI configured with sufficient permissions
#   - ACM certificate already issued and VALIDATED in us-east-1
#   - S3 bucket already created and has a public-read bucket policy
#   - python3 + cloudfront_site_config.py in same directory
#
# After running:
#   1. Note the CloudFront domain name in the output
#   2. Add CNAME record: @ → <cloudfront-domain>.cloudfront.net
#   3. Wait for DNS propagation (5-30 min)
#   4. Test: curl -I https://example.com
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Defaults ────────────────────────────────────────────────────────────────
REGION="us-east-1"
INCLUDE_WWW=""

# ── Argument parsing ─────────────────────────────────────────────────────────
usage() {
    echo "Usage: $0 --domain DOMAIN --bucket BUCKET --cert-arn CERT_ARN [--region REGION] [--include-www]"
    echo ""
    echo "Options:"
    echo "  --domain      Root domain name (e.g. example.com)"
    echo "  --bucket      S3 bucket name (usually same as domain)"
    echo "  --cert-arn    ACM certificate ARN (must be in us-east-1)"
    echo "  --region      S3 bucket region (default: us-east-1)"
    echo "  --include-www Also add www.domain alias to distribution"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain)     DOMAIN="$2"; shift 2 ;;
        --bucket)     BUCKET="$2"; shift 2 ;;
        --cert-arn)   CERT_ARN="$2"; shift 2 ;;
        --region)     REGION="$2"; shift 2 ;;
        --include-www) INCLUDE_WWW="--include-www"; shift ;;
        --help|-h)    usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

# Validate required args
[[ -z "${DOMAIN:-}" ]] && echo "❌ --domain is required" && usage
[[ -z "${BUCKET:-}" ]] && echo "❌ --bucket is required" && usage
[[ -z "${CERT_ARN:-}" ]] && echo "❌ --cert-arn is required" && usage

# ── Temp directory for generated files ─────────────────────────────────────
TMPDIR_WORK=$(mktemp -d)
DIST_CONFIG="$TMPDIR_WORK/cf-dist-config.json"
FUNCTION_CODE="$TMPDIR_WORK/url-rewrite.js"
FUNCTION_NAME="${DOMAIN//./-}-url-rewrite"

echo "═══════════════════════════════════════════════════════"
echo "  ClawWorks: New CloudFront + S3 Static Site Setup"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Domain:   $DOMAIN"
echo "  Bucket:   $BUCKET"
echo "  Region:   $REGION"
echo "  Cert ARN: $CERT_ARN"
echo ""

# ── Step 1: Validate ACM certificate ────────────────────────────────────────
echo "Step 1/5: Validating ACM certificate..."
CERT_STATUS=$(aws acm describe-certificate \
    --certificate-arn "$CERT_ARN" \
    --region us-east-1 \
    --query 'Certificate.Status' \
    --output text 2>&1)

if [[ "$CERT_STATUS" != "ISSUED" ]]; then
    echo "❌ Certificate status: $CERT_STATUS"
    echo "   The certificate must be ISSUED before CloudFront can use it."
    echo "   Add the CNAME validation record in your DNS provider, then retry."
    exit 1
fi
echo "   ✅ Certificate status: ISSUED"
echo ""

# ── Step 2: Generate distribution config + function code ───────────────────
echo "Step 2/5: Generating CloudFront configuration..."
python3 "$SCRIPT_DIR/cloudfront_site_config.py" \
    --domain "$DOMAIN" \
    --bucket "$BUCKET" \
    --cert-arn "$CERT_ARN" \
    --region "$REGION" \
    --out-config "$DIST_CONFIG" \
    --out-function "$FUNCTION_CODE" \
    $INCLUDE_WWW

echo ""

# ── Step 3: Create CloudFront Function (URL rewrite) ────────────────────────
echo "Step 3/5: Creating CloudFront Function: $FUNCTION_NAME..."

# Check if function already exists
EXISTING_FUNCTION=$(aws cloudfront describe-function \
    --name "$FUNCTION_NAME" \
    --query 'FunctionSummary.FunctionMetadata.FunctionARN' \
    --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$EXISTING_FUNCTION" != "NOT_FOUND" && "$EXISTING_FUNCTION" != "None" ]]; then
    echo "   ℹ️  Function $FUNCTION_NAME already exists: $EXISTING_FUNCTION"
    FUNCTION_ARN="$EXISTING_FUNCTION"
else
    FUNCTION_OUTPUT=$(aws cloudfront create-function \
        --name "$FUNCTION_NAME" \
        --function-config "{\"Comment\":\"Directory index rewrite for $DOMAIN\",\"Runtime\":\"cloudfront-js-2.0\"}" \
        --function-code "fileb://$FUNCTION_CODE" \
        --output json)

    FUNCTION_ARN=$(echo "$FUNCTION_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['FunctionSummary']['FunctionMetadata']['FunctionARN'])")
    echo "   ✅ Function created: $FUNCTION_ARN"

    # Publish the function (required before it can be associated)
    ETAG=$(echo "$FUNCTION_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['ETag'])")
    aws cloudfront publish-function \
        --name "$FUNCTION_NAME" \
        --if-match "$ETAG" > /dev/null
    echo "   ✅ Function published"
fi

# Inject the real function ARN into the distribution config
python3 -c "
import json
with open('$DIST_CONFIG') as f:
    config = json.load(f)
config['DefaultCacheBehavior']['FunctionAssociations']['Items'][0]['FunctionARN'] = '$FUNCTION_ARN'
with open('$DIST_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
print('   ✅ Function ARN injected into distribution config')
"
echo ""

# ── Step 4: Create CloudFront distribution ──────────────────────────────────
echo "Step 4/5: Creating CloudFront distribution..."
DIST_OUTPUT=$(aws cloudfront create-distribution \
    --distribution-config "file://$DIST_CONFIG" \
    --output json)

DIST_ID=$(echo "$DIST_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['Distribution']['Id'])")
DIST_DOMAIN=$(echo "$DIST_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['Distribution']['DomainName'])")
echo "   ✅ Distribution created"
echo "   ID:     $DIST_ID"
echo "   Domain: $DIST_DOMAIN"
echo ""

# Save dist ID for future deploys/invalidations
echo "$DIST_ID" > ".cloudfront-dist-id"
echo "   Saved to .cloudfront-dist-id"
echo ""

# ── Step 5: Print DNS instructions ──────────────────────────────────────────
echo "Step 5/5: Done!"
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ACTION REQUIRED: Configure DNS"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Add the following CNAME record in your DNS provider:"
echo ""
echo "  Type:  CNAME"
echo "  Host:  @  (root domain: $DOMAIN)"
echo "  Value: $DIST_DOMAIN"
echo "  TTL:   Automatic (or 300)"
echo ""
if [[ -n "$INCLUDE_WWW" ]]; then
echo "  Also add:"
echo "  Type:  CNAME"
echo "  Host:  www"
echo "  Value: $DIST_DOMAIN"
echo ""
fi
echo "  DNS propagation: 5–30 minutes"
echo "  Then test: curl -I https://$DOMAIN"
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Deployment"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  To deploy content, sync to S3 and invalidate cache:"
echo ""
echo "  aws s3 sync ./_site/ s3://$BUCKET/ --delete"
echo "  aws cloudfront create-invalidation --distribution-id $DIST_ID --paths '/*'"
echo ""
echo "  Or use the bundled deploy-to-s3.sh script if available."
echo ""

# Cleanup temp dir
rm -rf "$TMPDIR_WORK"
