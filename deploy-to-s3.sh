#!/bin/bash

set -e

echo "=== Deploying to AWS S3 + CloudFront ==="
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

# 3. Sync to S3
echo "3. Syncing files to S3..."
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

echo "✓ Files synced to S3"
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
echo "Creating invalidation..."

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
echo "✓ Changes will be live in 1-3 minutes"

echo ""
echo "5. Verifying deployment..."
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
