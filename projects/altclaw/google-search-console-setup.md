# Google Search Console Setup

**URL:** https://search.google.com/search-console

## Step-by-Step Setup

### 1. Add Property
- Go to search.google.com/search-console
- Click "Add Property"
- Choose "URL prefix" (not "Domain")
- Enter: `https://bughuntertools.com`
- Click "Continue"

### 2. Verify Ownership

**Method A: HTML Tag (Easiest)**
- Google will show: `<meta name="google-site-verification" content="XXXXX">`
- Send me that meta tag
- I'll add it to the site
- Click "Verify"

**Method B: DNS (Alternative)**
- Add TXT record to Namecheap DNS
- Value: google-site-verification=XXXXX
- Wait 10 minutes, click "Verify"

### 3. Submit Sitemap
Once verified:
- Click "Sitemaps" in left sidebar
- Enter: `sitemap.xml`
- Click "Submit"

Google will crawl your site within 24-48 hours.

## What Search Console Tracks

### Immediate (Day 1)
- Indexing status (which pages Google found)
- Any errors preventing indexing
- Manual actions (penalties)

### After 2-3 Days
- Search impressions (how often site appears in Google)
- Click-through rate
- Average position for keywords
- Which queries trigger your pages

### Key Reports

**Performance Report:**
- Total clicks
- Total impressions
- Average CTR (click-through rate)
- Average position
- **Filter by:** Queries, Pages, Countries, Devices

**URL Inspection:**
- Check if specific page is indexed
- See how Google sees your page
- Request indexing (forces crawl)

**Coverage Report:**
- Which pages are indexed
- Which pages have errors
- Which pages are excluded

## Weekly Checklist

**Every Monday:**
1. Check "Performance" for new rankings
2. Look for indexing errors in "Coverage"
3. Review top queries driving traffic
4. Check average position trends

## Expected Timeline

**Week 1 (Feb 8-15):**
- Setup and verification
- Submit sitemap
- Google discovers site

**Week 2-3:**
- First pages indexed
- Site appears in search results (but not ranking yet)
- 0-10 impressions/day

**Week 4-8:**
- Rankings start appearing
- Long-tail keywords rank first
- 10-100 impressions/day

**Month 3-6:**
- Main keywords ranking (position 20-50)
- 100-500 impressions/day
- First significant organic traffic

## Target Keywords to Track

**Main keywords (harder to rank):**
- bug bounty tools
- security testing tools
- penetration testing tools
- best bug bounty tools 2026

**Long-tail keywords (easier to rank):**
- bug bounty starter kit
- best wifi adapter for pentesting
- bug bounty books for beginners
- how to start bug bounty hunting
- raspberry pi penetration testing

## Pro Tips

1. **Request indexing for new pages:** Use URL Inspection tool → "Request Indexing"
2. **Fix errors immediately:** If Coverage shows errors, fix ASAP
3. **Monitor CTR:** If impressions high but clicks low, improve title/description
4. **Track competitors:** Search for "bug bounty tools" and note who ranks top 10

## Integration with Analytics

Search Console + Google Analytics = complete picture:
- **Search Console:** How you're found (keywords, positions)
- **Analytics:** What happens after they arrive (bounces, conversions)

Cross-reference data weekly.

---

**Status:** Sitemap ready at https://bughuntertools.com/sitemap.xml  
**Next:** Verify ownership in Search Console, submit sitemap  
**Expected indexing:** 24-48 hours after submission
