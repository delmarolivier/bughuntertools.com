#!/bin/bash

# full-sync-to-s3.sh — EXPLICIT FULL SYNC with --delete
#
# ⚠️  USE WITH CAUTION. This script DELETES files from S3 that are not in _site/.
#
# When to use:
#   - Removing an article that has been deliberately retired (source .njk also removed)
#   - After a major site restructure where old paths are intentionally obsolete
#   - Cleaning up a test/staging deployment
#
# NEVER use this without first confirming that ALL published articles have a
# corresponding .njk source file in src/articles/ (see PUBLISHING_WORKFLOW.md).
#
# Standard incremental deploys: use deploy-to-s3.sh (no --delete).

set -e

echo "=== FULL SYNC — bughuntertools.com → S3 (with --delete) ==="
echo ""
echo "⚠️  WARNING: This will DELETE S3 objects not present in _site/"
echo ""
read -r -p "Have you verified all published articles exist as .njk sources in src/articles/? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted. Run 'ls src/articles/' to audit sources before full sync."
    exit 1
fi
echo ""

# Configuration
BUCKET="bughuntertools.com"
REGION="us-east-1"
SITE_DIR="/home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com"

cd "$SITE_DIR"

# 1. Build site with 11ty
echo "1. Building site with 11ty..."
npx @11ty/eleventy
echo "✓ Site built to _site/"
echo ""

# 2. Run quality checks
echo "2. Running quality checks..."
cd _site
../check-quality.sh
if [ $? -ne 0 ]; then
    echo "❌ Quality checks failed - fix errors before deploying"
    exit 1
fi
cd ..
echo "✓ Quality checks passed"
echo ""

# 3. Full sync to S3 (with --delete)
echo "3. Full sync to S3 (--delete enabled)..."
aws s3 sync _site/ s3://$BUCKET/ \
  --region $REGION \
  --exclude ".git/*" \
  --exclude "*.sh" \
  --exclude "*.md" \
  --exclude "*.json" \
  --exclude "*.py" \
  --exclude "node_modules/*" \
  --exclude "src/*" \
  --exclude ".eleventy.js" \
  --cache-control "public, max-age=3600" \
  --delete

echo "✓ Full sync complete — S3 now mirrors _site/ exactly"
echo ""

# 4. Invalidate CloudFront cache (MANDATORY)
echo "4. Invalidating CloudFront cache..."
DIST_ID=$(cat .cloudfront-dist-id 2>/dev/null || echo "")

if [ -z "$DIST_ID" ]; then
    echo "❌ ERROR: No CloudFront distribution ID found"
    echo "Create .cloudfront-dist-id file with distribution ID"
    exit 1
fi

echo "Distribution: $DIST_ID"
INVALIDATION_OUTPUT=$(aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ CloudFront invalidation FAILED:"
    echo "$INVALIDATION_OUTPUT"
    exit 1
fi

INVALIDATION_ID=$(echo "$INVALIDATION_OUTPUT" | grep -o '"Id": "[^"]*"' | cut -d'"' -f4)
echo "✓ CloudFront cache invalidated (ID: $INVALIDATION_ID)"
echo ""
echo "✅ Full sync deployment complete!"
