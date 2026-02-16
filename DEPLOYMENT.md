# DEPLOYMENT PROCESS - MANDATORY

## ⚠️ CRITICAL: ONLY Use deploy-to-s3.sh

**DO NOT manually sync files to S3.**  
**DO NOT skip CloudFront invalidation.**  
**DO NOT use any other deployment method.**

## The ONLY Correct Way to Deploy

```bash
cd /home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com
./deploy-to-s3.sh
```

This script:
1. Builds the site with 11ty
2. Runs quality checks
3. Syncs to S3
4. **Invalidates CloudFront cache (MANDATORY)**
5. Verifies deployment

## Why This Matters

**Problem:** CloudFront caches pages for hours. If you upload new content to S3 without invalidating CloudFront, visitors see OLD content.

**Solution:** The deploy script automatically creates a CloudFront invalidation after every S3 upload.

**What happens if you skip this:**
- S3 has new content
- CloudFront serves old content
- Delmar sees outdated site
- Trust lost

## Script Enforcement

The deploy script will **EXIT WITH ERROR** if:
- CloudFront distribution ID missing (`.cloudfront-dist-id` file)
- CloudFront invalidation command fails
- AWS credentials invalid

**If the script fails, deployment is incomplete. DO NOT proceed.**

## For Subagents

If you are writing code to deploy this site:
1. Call `./deploy-to-s3.sh` 
2. Check exit code (must be 0)
3. Verify "✓ CloudFront cache invalidated" appears in output
4. If script fails, report error - don't deploy manually

## Troubleshooting

**Error: "No CloudFront distribution ID found"**
- Create `.cloudfront-dist-id` file with: `EPZKYF6ET4DPI`

**Error: "CloudFront invalidation FAILED"**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify CloudFront permissions

**Script hangs or times out:**
- Check internet connection
- Verify AWS service status

## Verification

After deployment, verify:
1. Script output shows: `✓ CloudFront cache invalidated (ID: ...)`
2. Wait 1-3 minutes for invalidation to complete
3. Check live site: https://bughuntertools.com
4. Verify latest article appears first

## Last Updated

February 14, 2026 - 23:06 GMT  
Fixed by: Jeff (CTO)  
Reason: CloudFront invalidation was optional, causing stale content
