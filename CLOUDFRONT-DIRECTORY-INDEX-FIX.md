# CloudFront Directory Index Fix

## Problem
When accessing `https://bughuntertools.com/articles/` (directory URL ending with `/`), CloudFront was serving the root `index.html` instead of `articles/index.html`.

**Root cause:** CloudFront's `DefaultRootObject` only applies to the root path `/`, not subdirectories. When using CloudFront with S3 Origin Access Identity (OAI), directory index files are not automatically served.

## Solution
Created a CloudFront Function to rewrite URLs:
- `/articles/` → `/articles/index.html`
- `/articles` → `/articles/index.html`
- Any directory URL gets `index.html` appended

## Implementation

### 1. CloudFront Function Created
**Function Name:** `bughuntertools-url-rewrite`  
**ARN:** `arn:aws:cloudfront::172337538645:function/bughuntertools-url-rewrite`  
**Runtime:** cloudfront-js-2.0  
**Event Type:** viewer-request

**Code:**
```javascript
function handler(event) {
    var request = event.request;
    var uri = request.uri;
    
    // If URI ends with '/', append 'index.html'
    if (uri.endsWith('/')) {
        request.uri += 'index.html';
    }
    // If URI has no file extension, append '/index.html'
    else if (!uri.includes('.')) {
        request.uri += '/index.html';
    }
    
    return request;
}
```

### 2. Associated with Distribution
- Distribution ID: EPZKYF6ET4DPI
- Applied to: DefaultCacheBehavior
- Event type: viewer-request (runs before cache lookup)

### 3. Deployment Status
- Initiated: 2026-02-09 10:42 GMT
- Status: InProgress (5-15 min propagation time)
- New ETag: E1F83G8C2ARO7P

## Testing

Once deployment completes (check status with `aws cloudfront get-distribution --id EPZKYF6ET4DPI --query 'Distribution.Status'`):

```bash
# These should all work and serve correct content:
curl -I https://bughuntertools.com/articles/
curl -I https://bughuntertools.com/articles
curl -I https://bughuntertools.com/

# Verify correct content is served:
curl -s https://bughuntertools.com/articles/ | grep -q "All Bug Bounty Guides" && echo "✅ Articles index works"
```

## Why CloudFront Functions vs Lambda@Edge?

**CloudFront Functions:**
- ✅ Runs on all CloudFront edge locations (cheaper, faster)
- ✅ Sub-millisecond execution
- ✅ $0.10 per 1M invocations
- ✅ Perfect for simple URL rewrites
- ❌ Limited to 10KB code, no network calls

**Lambda@Edge:**
- ❌ More expensive ($0.60 per 1M + compute time)
- ❌ Runs in regional edge caches (fewer locations)
- ✅ Full Node.js runtime
- ✅ Can make network requests

For URL rewriting, CloudFront Functions are the correct choice.

## Alternative Solutions (Not Used)

### Option 1: S3 Website Hosting
Enable S3 website hosting mode which handles directory indexes automatically.

**Rejected because:**
- Cannot use Origin Access Identity (OAI) with website hosting
- Must make bucket publicly readable
- Less secure

### Option 2: Create Copies
Create `/articles` file (without extension) as copy of `/articles/index.html`

**Rejected because:**
- Duplicate content maintenance
- SEO issues with multiple URLs
- No trailing slash normalization

## Files Created
- `cloudfront-function-url-rewrite.js` - Function source code
- `cf-dist-config.json` - Original distribution config
- `cf-dist-config-updated.json` - Updated distribution config

## Deployment Date
2026-02-09 10:42 GMT

## Status
✅ Function created and published  
⏳ Distribution update in progress (wait 5-15 minutes)  
⬜ Testing after propagation
