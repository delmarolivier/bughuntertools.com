#!/bin/bash

# Wait for ACM certificate validation and create CloudFront distribution

CERT_ARN="arn:aws:acm:us-east-1:172337538645:certificate/6151eb1b-9f1f-4dba-a4ae-e52abe45cb91"
BUCKET="bughuntertools.com"
REGION="us-east-1"

echo "Checking certificate status..."
STATUS=$(aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --output text)

echo "Status: $STATUS"

if [ "$STATUS" != "ISSUED" ]; then
    echo "Certificate not validated yet. Will check again in 5 minutes."
    exit 0
fi

echo "✅ Certificate validated!"
echo ""
echo "Creating CloudFront distribution..."

# Create distribution config
cat > /tmp/cf-config.json << 'EOF'
{
  "CallerReference": "bughuntertools-2026-02-08",
  "Comment": "bughuntertools.com static site",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-bughuntertools",
        "DomainName": "bughuntertools.com.s3.us-east-1.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-bughuntertools",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 3600,
    "MaxTTL": 86400
  },
  "Aliases": {
    "Quantity": 1,
    "Items": ["bughuntertools.com"]
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "arn:aws:acm:us-east-1:172337538645:certificate/6151eb1b-9f1f-4dba-a4ae-e52abe45cb91",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 403,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  }
}
EOF

# Create distribution
DIST_OUTPUT=$(aws cloudfront create-distribution \
  --distribution-config file:///tmp/cf-config.json \
  --output json 2>&1)

if echo "$DIST_OUTPUT" | grep -q "DomainName"; then
    DIST_DOMAIN=$(echo "$DIST_OUTPUT" | jq -r '.Distribution.DomainName')
    DIST_ID=$(echo "$DIST_OUTPUT" | jq -r '.Distribution.Id')
    
    echo "✅ CloudFront distribution created!"
    echo ""
    echo "Distribution ID: $DIST_ID"
    echo "CloudFront Domain: $DIST_DOMAIN"
    echo ""
    echo "ACTION REQUIRED:"
    echo "================"
    echo "Add this CNAME record to Namecheap:"
    echo ""
    echo "Type:  CNAME"
    echo "Host:  @  (or bughuntertools.com)"
    echo "Value: $DIST_DOMAIN"
    echo "TTL:   Automatic"
    echo ""
    echo "After DNS propagates (5-30 min), site will be live at:"
    echo "https://bughuntertools.com"
    
    # Save for future deploys
    echo "$DIST_ID" > /home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com/.cloudfront-dist-id
else
    echo "❌ Error creating distribution:"
    echo "$DIST_OUTPUT"
    exit 1
fi
