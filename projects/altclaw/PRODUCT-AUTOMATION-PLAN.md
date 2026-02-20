# AltClaw Product Automation Plan

**Problem:** Manual product management doesn't scale. Need to automate discovery, validation, and maintenance.

**Created:** 2026-02-11

---

## Current Gaps

1. ❌ Products added manually from PRODUCT-RESEARCH.md
2. ❌ check-quality.sh has hardcoded ASIN list (8 ASINs, actual: 13)
3. ❌ No automated product discovery from research
4. ❌ No periodic re-validation of products

---

## Solution Architecture

### 1. Dynamic ASIN Validation (IMMEDIATE)

**Current:** Hardcoded list in check-quality.sh
```bash
VALID_ASINS=(
    "1118026470"
    "B005LVQA9S"
    # ... 8 total
)
```

**New:** Extract ASINs from VALIDATED_PRODUCTS.md dynamically
```bash
# Extract all ASINs from VALIDATED_PRODUCTS.md
VALID_ASINS=$(grep -oP '(?<=\*\*ASIN:\*\* )[A-Z0-9]{10}' VALIDATED_PRODUCTS.md)
```

**Benefits:**
- Single source of truth (VALIDATED_PRODUCTS.md)
- No drift between product list and validation
- Automatically picks up new products

---

### 2. Weekly Product Discovery (AUTOMATED)

**Schedule:** Every Monday 11:00 GMT (after daily research)

**Process:**
1. Read last 7 days of research files (projects/security/research/2026-02-*.md)
2. Extract product mentions:
   - Tools mentioned (e.g., "Burp Suite Professional")
   - Hardware recommendations (e.g., "WiFi adapters")
   - Books cited
   - Laptop/device requirements
3. Cross-reference with VALIDATED_PRODUCTS.md (avoid duplicates)
4. For new product candidates:
   - Search Amazon for ASIN
   - Verify availability + price
   - Check if credible source exists (research citation)
   - Calculate commission
5. Add validated products to VALIDATED_PRODUCTS.md
6. Update check-quality.sh ASIN list automatically
7. Report weekly additions (e.g., "Added 3 new products this week")

**Output:**
- Updated VALIDATED_PRODUCTS.md
- Git commit with "Auto-add: [Product Name] from [Source]"
- Telegram notification to AltClaw group

---

### 3. Monthly Product Verification (AUTOMATED)

**Schedule:** First Monday of month, 12:00 GMT

**Process:**
1. Read all ASINs from VALIDATED_PRODUCTS.md
2. For each product:
   - Check Amazon availability (HTTP 200 on product page)
   - Scrape current price
   - Compare to documented price (flag if >20% change)
   - Verify affiliate link format (tag=altclaw-20)
3. Flag issues:
   - ❌ Product no longer available (HTTP 404)
   - ⚠️ Price changed significantly
   - ❌ Out of stock
4. Generate verification report
5. Update VALIDATED_PRODUCTS.md with new prices
6. Archive deprecated products to DEPRECATED_PRODUCTS.md

**Output:**
- Updated prices in VALIDATED_PRODUCTS.md
- Verification report (projects/altclaw/product-verification/YYYY-MM.md)
- Telegram alert if products removed

---

## Implementation Priority

### Phase 1: Critical Fix (TODAY)
- ✅ Fix check-quality.sh to read ASINs from VALIDATED_PRODUCTS.md
- ✅ Create extract-asins.sh helper script
- ✅ Test with current 13 products

### Phase 2: Discovery Automation (THIS WEEK)
- Create product-discovery.py script
- Add weekly cron job (Monday 11:00 GMT)
- Test with last week's research findings

### Phase 3: Verification Automation (THIS MONTH)
- Create product-verification.py script
- Add monthly cron job (First Monday 12:00 GMT)
- Implement price tracking

---

## Scripts to Create

### extract-asins.sh
```bash
#!/bin/bash
# Extract all ASINs from VALIDATED_PRODUCTS.md
grep -oP '(?<=\*\*ASIN:\*\* )[A-Z0-9]{10}' VALIDATED_PRODUCTS.md | sort -u
```

### product-discovery.py
```python
# Scan recent research files
# Extract product mentions
# Search Amazon API / scrape for ASINs
# Validate and add to VALIDATED_PRODUCTS.md
```

### product-verification.py
```python
# Read all ASINs from VALIDATED_PRODUCTS.md
# Check availability on Amazon
# Update prices
# Flag deprecated products
```

---

## Cron Jobs to Add

### Weekly Product Discovery
```
Name: AltClaw: Weekly Product Discovery
Schedule: 0 11 * * 1 (Monday 11:00 GMT)
Task: Run product-discovery.py, commit new products, notify Telegram
```

### Monthly Product Verification
```
Name: AltClaw: Monthly Product Verification
Schedule: 0 12 * * 1 (First Monday 12:00 GMT, conditional)
Task: Run product-verification.py, update prices, archive deprecated
```

---

## Success Metrics

**Week 1:**
- check-quality.sh uses dynamic ASIN list (no more drift)
- Weekly discovery runs successfully
- At least 1-3 new products added automatically

**Month 1:**
- 20+ products validated (manual + automated)
- First monthly verification completes
- Zero stale ASINs in quality checks

**Month 3:**
- 50+ products (per PRODUCT-RESEARCH.md plan)
- Fully automated pipeline (no manual ASIN hunting)
- Price tracking shows product value trends

---

## Risk Mitigation

**Amazon API Rate Limits:**
- Use scraping with backoff (not official API)
- Run weekly/monthly (low frequency)
- Cache results locally

**False Positives:**
- Human review before final commit
- Product discovery creates draft entries
- Weekly review of new additions

**Deprecated Products:**
- Archive to DEPRECATED_PRODUCTS.md (don't delete)
- Keep commission history for analytics
- Replace with similar alternatives when possible

---

**Next Action:** Implement Phase 1 (fix check-quality.sh) immediately.
