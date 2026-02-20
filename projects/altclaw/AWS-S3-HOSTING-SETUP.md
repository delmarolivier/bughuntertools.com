# AWS S3 Static Website Hosting Setup Guide

## Architecture

**Components:**
- **S3 Bucket:** Static file storage
- **CloudFront:** CDN + HTTPS (S3 static hosting doesn't support HTTPS natively)
- **Route53:** DNS (or Namecheap if you prefer)
- **ACM:** SSL certificate (free with AWS)

**Why CloudFront?**
- S3 static website hosting doesn't support HTTPS
- CloudFront provides CDN (faster global access)
- Free SSL certificate via ACM
- Better for AI bot crawlers (lower latency)

---

## Setup Steps

### 1. Create S3 Bucket

```bash
aws s3 mb s3://bughuntertools.com --region us-east-1
```

**Note:** Bucket name must match domain name for static website hosting.

### 2. Configure Static Website Hosting

```bash
aws s3 website s3://bughuntertools.com \
  --index-document index.html \
  --error-document index.html
```

### 3. Set Bucket Policy (Public Read)

Create `bucket-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::bughuntertools.com/*"
    }
  ]
}
```

Apply:
```bash
aws s3api put-bucket-policy \
  --bucket bughuntertools.com \
  --policy file://bucket-policy.json
```

### 4. Request SSL Certificate (ACM)

```bash
# Must be in us-east-1 for CloudFront
aws acm request-certificate \
  --domain-name bughuntertools.com \
  --validation-method DNS \
  --region us-east-1
```

**Output:** Certificate ARN (save this)

### 5. Validate Certificate

List validation records:
```bash
aws acm describe-certificate \
  --certificate-arn <ARN> \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord'
```

Add CNAME record to Namecheap DNS (or Route53 if migrating).

### 6. Create CloudFront Distribution

```bash
aws cloudfront create-distribution \
  --origin-domain-name bughuntertools.com.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html
```

*(See full config in deploy script)*

### 7. Update DNS

**If using Namecheap:**
- CNAME: bughuntertools.com → <cloudfront-distribution>.cloudfront.net

**If migrating to Route53:**
- Create hosted zone
- Point A record to CloudFront distribution (alias)

---

## Deployment Script

Created: `deploy-to-s3.sh`

**What it does:**
1. Runs quality checks
2. Syncs files to S3
3. Invalidates CloudFront cache
4. Verifies deployment

**Usage:**
```bash
./deploy-to-s3.sh
```

---

## Cost Estimate (AWS Free Tier)

- **S3:** $0.023/GB storage (~$0.01/month for this site)
- **CloudFront:** 50GB free/month (more than enough)
- **Route53:** $0.50/month per hosted zone (optional)
- **ACM:** FREE

**Total:** ~$0.01-0.50/month (vs Netlify $19/month)

---

## Workflow

**Before (Netlify):**
```
git push → Netlify auto-deploys
```

**After (S3):**
```
git commit
./check-quality.sh  # validate
./deploy-to-s3.sh   # sync to S3
git push            # backup to GitHub
```

**Or automate via GitHub Actions** (future enhancement).

---

## Next Steps

1. Run setup commands above
2. Wait for ACM certificate validation (~5-10 min)
3. Create CloudFront distribution
4. Update DNS
5. Test: https://bughuntertools.com
6. Delete Netlify deployment

---

## Troubleshooting

**Issue:** Certificate validation stuck
**Fix:** Verify CNAME record added to DNS (check `dig _<random>.bughuntertools.com`)

**Issue:** CloudFront shows old content
**Fix:** Run invalidation: `aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"`

**Issue:** 403 Forbidden
**Fix:** Check S3 bucket policy allows public read

---

**Status:** Ready to implement
**Estimated setup time:** 15-20 minutes (mostly waiting for ACM validation)
