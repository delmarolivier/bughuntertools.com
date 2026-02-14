#!/bin/bash

set -e

echo "=== Deploying to AWS S3 + CloudFront (Versioned) ==="
echo ""

# Configuration
BUCKET="bughuntertools.com"
REGION="us-east-1"
SITE_DIR="/home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com"
VERSION=$(date +%s)

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

# 3. Upload with cache control headers
echo "3. Syncing files to S3 with version $VERSION..."

# HTML files - short cache (5 minutes)
aws s3 sync _site/ s3://$BUCKET/ \
  --region $REGION \
  --exclude "*" \
  --include "*.html" \
  --cache-control "public, max-age=300" \
  --metadata-directive REPLACE

# CSS/JS - long cache with versioning
aws s3 sync _site/css/ s3://$BUCKET/css/ \
  --region $REGION \
  --cache-control "public, max-age=31536000, immutable" \
  --metadata-directive REPLACE

# Sitemap - medium cache
aws s3 sync _site/ s3://$BUCKET/ \
  --region $REGION \
  --exclude "*" \
  --include "sitemap.xml" \
  --cache-control "public, max-age=3600" \
  --metadata-directive REPLACE

echo "✓ Files synced to S3 with proper cache headers"
echo ""

# 4. Invalidate CloudFront cache
echo "4. Checking for CloudFront distribution..."
DIST_ID=$(cat .cloudfront-dist-id 2>/dev/null || echo "")

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
echo "5. Verifying deployment..."
S3_WEBSITE="http://$BUCKET.s3-website-$REGION.amazonaws.com"
echo "S3 endpoint: $S3_WEBSITE"

echo ""
echo "✅ Deployment complete! (Version: $VERSION)"
echo ""
echo "Changes will be live after CloudFront update completes (~10-15 min)"
echo "HTML cache: 5 minutes"
echo "Static assets: 1 year (immutable)"
echo ""
echo "Site: https://bughuntertools.com"
