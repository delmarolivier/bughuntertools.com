# Analytics & AI Tracking Guide

**Google Analytics ID:** G-PP6M3SZSVR  
**Dashboard:** https://analytics.google.com  
**Status:** ✅ Live on all pages

---

## What Google Analytics Tracks

### Standard Metrics (Available Now)
- **Visitors:** Total unique visitors
- **Page views:** How many times pages are viewed
- **Sessions:** Visit duration and engagement
- **Traffic sources:** Where visitors come from (Google, direct, social)
- **Bounce rate:** % who leave after 1 page
- **Pages per session:** Average pages viewed
- **Demographics:** Age, location, device type

### How to Access
1. Go to analytics.google.com
2. Select "Bug Hunter Tools" property
3. View "Reports" → "Realtime" to see live visitors
4. View "Reports" → "Acquisition" to see traffic sources

---

## Tracking AI Search Engine Access

### AI Bot User Agents to Watch For

**ChatGPT:**
- `ChatGPT-User`
- `GPTBot`

**Perplexity:**
- `PerplexityBot`

**Claude (Anthropic):**
- `Claude-Web`
- `anthropic-ai`

**Google Gemini:**
- `Google-Extended`

**Bing AI:**
- `bingbot` (with AI context)

### How to See AI Bot Traffic in Google Analytics

**Method 1: Exploration Reports (Advanced)**
1. Go to "Explore" in GA4
2. Create new exploration
3. Dimensions: Add "User agent"
4. Filter for bot names above
5. See which AI bots visited

**Method 2: BigQuery Export (Free tier available)**
- Export GA4 data to BigQuery
- Query for specific user agents
- More detailed analysis

**Method 3: Manual Check (Weekly)**
Test if AI cites your content:
```
Ask ChatGPT: "What are the best bug bounty tools?"
Ask Perplexity: "Best security testing tools 2026"
Ask Claude: "Recommend bug bounty hunter tools"
```

See if they cite bughuntertools.com

---

## Traffic Milestones to Watch

### Week 1 (Feb 8-15, 2026)
- **Expected:** 10-50 visitors (mostly you checking it)
- **Goal:** Verify Analytics working
- **Action:** Check "Realtime" report to see yourself

### Month 1 (Feb 8 - Mar 8)
- **Expected:** 50-200 visitors
- **Sources:** Direct traffic, initial SEO
- **Goal:** First organic Google visitors
- **AI Citations:** Likely 0 (too new)

### Month 2 (Mar 8 - Apr 8)
- **Expected:** 200-500 visitors
- **Sources:** Organic search growing
- **Goal:** Top 20 ranking for 2-3 keywords
- **AI Citations:** Possible (if content quality high)

### Month 3 (Apr 8 - May 8)
- **Expected:** 500-1,000 visitors
- **Sources:** Majority organic search
- **Goal:** Top 10 ranking for 5+ keywords
- **AI Citations:** 1-3 mentions expected

---

## How AI Search Engines Find Your Content

### 1. Web Crawling
- AI bots crawl your site like Google
- They index content for their knowledge base
- **You can't control when they visit**

### 2. Citation Triggers
**What makes AI cite your content:**
- ✅ Comprehensive, detailed content (3000+ words)
- ✅ Structured with clear headings
- ✅ Lists, tables, comparisons
- ✅ FAQ sections
- ✅ Up-to-date information (2026 in title)
- ✅ Schema.org markup (you have this ✅)
- ✅ Authority signals (links, mentions)

### 3. Referrer Data
When users click AI-generated links:
- Some AI tools send referrer: `perplexity.ai`
- Google Analytics captures this
- Shows in "Acquisition" → "Traffic acquisition"

---

## Premium AI Citation Tracking Tools

### Ahrefs Brand Radar
**Price:** $99-199/month  
**What it does:**
- Tracks mentions in ChatGPT/Perplexity
- Alerts when you're cited
- Shows exact queries that trigger citations
- Competitive analysis

**When to get it:** Month 6+ (when you have traffic)

### Snezzi
**Price:** ~$50/month  
**What it does:**
- Similar to Ahrefs but cheaper
- Perplexity citation tracking
- Basic ChatGPT monitoring

**When to get it:** Month 3-6 (if seeing early citations)

### Manual Tracking (FREE)
**Weekly checklist:**
```
Monday morning:
1. Search "bughuntertools.com" in Perplexity
2. Ask ChatGPT: "best bug bounty tools 2026"
3. Check if your site appears
4. Document in spreadsheet
```

---

## Key Reports to Check Weekly

### 1. Realtime Report
**Location:** Reports → Realtime  
**What to check:**
- Are people on the site right now?
- Which pages are they viewing?
- Where are they from?

### 2. Traffic Acquisition
**Location:** Reports → Acquisition → Traffic acquisition  
**What to check:**
- Organic search traffic growing?
- Any referral traffic from AI tools?
- Direct traffic vs organic ratio

### 3. Pages and Screens
**Location:** Reports → Engagement → Pages and screens  
**What to check:**
- Which pages get most views?
- Books section getting clicks?
- High bounce rate on any page?

### 4. Events
**Location:** Reports → Engagement → Events  
**What to check:**
- Scroll depth
- Outbound clicks (to Amazon)
- Time on page

---

## Custom Events to Track (Optional)

You can add custom tracking for:
- **Amazon link clicks:** Track each affiliate click
- **Book section views:** How many see the books?
- **Newsletter signups:** If you add form functionality

Example custom event code:
```javascript
// Track Amazon link clicks
gtag('event', 'click', {
  'event_category': 'affiliate',
  'event_label': 'amazon_book_click'
});
```

(I can add this later if you want detailed click tracking)

---

## What Success Looks Like

### Month 1
- ✅ 50+ visitors
- ✅ Analytics working correctly
- ✅ No AI citations yet (normal)

### Month 3
- ✅ 500+ visitors
- ✅ Organic search = 60%+ of traffic
- ✅ 1-3 AI citations detected

### Month 6
- ✅ 2,000+ visitors
- ✅ Multiple AI citations
- ✅ Referral traffic from perplexity.ai visible
- ✅ Consider Ahrefs/Snezzi subscription

---

## Action Items

**Today:**
- ✅ Analytics installed
- ✅ Tracking ID: G-PP6M3SZSVR
- [ ] Check "Realtime" report to verify working

**This Week:**
- [ ] Visit site yourself, watch realtime data update
- [ ] Check "Acquisition" report (will be mostly empty)
- [ ] Set up weekly Monday morning check-in

**Monthly:**
- [ ] Review traffic trends
- [ ] Check for AI bot user agents
- [ ] Test manual AI citations
- [ ] Document growth in spreadsheet

---

**Current Status:** Analytics live, ready to track!  
**Next Check:** Monday, Feb 10, 2026 (first full week of data)
