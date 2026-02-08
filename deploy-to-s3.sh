#!/bin/bash

set -e

echo "=== Deploying to AWS S3 + CloudFront ==="
echo ""

# Configuration
BUCKET="bughuntertools.com"
REGION="us-east-1"
SITE_DIR="/home/delmar/.openclaw/workspace/projects/altclaw/bughuntertools.com"

cd "$SITE_DIR"

# 1. Run quality checks
echo "1. Running quality checks..."
./check-quality.sh
if [ $? -ne 0 ]; then
    echo "❌ Quality checks failed - fix errors before deploying"
    exit 1
fi
echo "✓ Quality checks passed"
echo ""

# 2. Sync to S3
echo "2. Syncing files to S3..."
aws s3 sync . s3://$BUCKET/ \
  --region $REGION \
  --exclude ".git/*" \
  --exclude "*.sh" \
  --exclude "*.md" \
  --exclude "bucket-policy.json" \
  --exclude "VALIDATED_PRODUCTS.md" \
  --exclude "node_modules/*" \
  --cache-control "public, max-age=3600" \
  --delete

echo "✓ Files synced to S3"
echo ""

# 3. Invalidate CloudFront cache (if distribution exists)
echo "3. Checking for CloudFront distribution..."
DIST_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[0].DomainName=='$BUCKET.s3.amazonaws.com'].Id" --output text 2>/dev/null)

if [ -n "$DIST_ID" ]; then
    echo "Found distribution: $DIST_ID"
    echo "Creating cache invalidation..."
    aws cloudfront create-invalidation \
      --distribution-id $DIST_ID \
      --paths "/*" > /dev/null
    echo "✓ CloudFront cache invalidated"
else
    echo "⚠️  No CloudFront distribution found (will create later)"
fi

echo ""
echo "4. Verifying deployment..."
S3_WEBSITE="http://$BUCKET.s3-website-$REGION.amazonaws.com"
echo "S3 endpoint: $S3_WEBSITE"

# Test if site is accessible
if curl -s -o /dev/null -w "%{http_code}" "$S3_WEBSITE" | grep -q "200"; then
    echo "✓ Site is live at S3 endpoint"
else
    echo "⚠️  Site might not be accessible yet (check bucket policy)"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set up CloudFront distribution (if not done)"
echo "2. Request ACM certificate"
echo "3. Update DNS to point to CloudFront"
echo ""
echo "Site will be live at: https://bughuntertools.com"
