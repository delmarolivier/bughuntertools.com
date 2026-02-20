# AI Agent Referrer Tracking - Implementation

**Deployed:** February 14, 2026 09:30 GMT  
**Git Commit:** ef22cb1  
**Priority:** P0 (Revenue-critical measurement)

---

## What It Tracks

JavaScript code in `base.njk` template detects and tracks visits from AI agents.

### Detected AI Sources

**Primary AI Assistants (User-Agent + Referrer):**
- `chatgpt` - ChatGPT web browsing
- `claude` - Claude AI
- `perplexity` - Perplexity AI
- `google_gemini` - Google Gemini/Bard

**AI Crawlers (User-Agent only):**
- `openai_crawler` - GPTBot (OpenAI's crawler)
- `anthropic_crawler` - ClaudeBot/Anthropic-AI

### GA4 Event Structure

**Event Name:** `ai_agent_visit`

**Event Parameters:**
- `ai_source` - Which AI agent (chatgpt, claude, perplexity, etc.)
- `page_path` - Which article they visited
- `user_agent` - Full User-Agent string for debugging

**Custom Dimension:** `ai_visitor` set to AI source value

---

## How to View in Google Analytics 4

### Method 1: Custom Event Report

1. Go to GA4 → Reports → Engagement → Events
2. Search for event: `ai_agent_visit`
3. Click event name to see details
4. View event parameters: `ai_source`, `page_path`

### Method 2: Exploration Report

1. GA4 → Explore → Create new exploration
2. Technique: Free form
3. Dimensions: Add `Event name`, `ai_source` (custom parameter)
4. Metrics: Add `Event count`
5. Rows: Drag `ai_source`
6. Values: Drag `Event count`
7. Filters: Add `Event name` = `ai_agent_visit`

**Result:** See count of AI agent visits by source.

### Method 3: Real-Time Tracking

1. GA4 → Reports → Real-time
2. Look for event: `ai_agent_visit`
3. See AI traffic as it happens (useful for testing)

---

## Validation & Testing

### Test ChatGPT Detection

1. Ask ChatGPT: "What are the best bug bounty tools?"
2. If ChatGPT cites bughuntertools.com → visit will be tracked
3. Check GA4 Real-time → Events → `ai_agent_visit`
4. Should see `ai_source: chatgpt`

### Test Claude Detection

1. Ask Claude: "Recommend security testing books"
2. If Claude browses bughuntertools.com → tracked
3. Check GA4 for `ai_source: claude`

### Test Perplexity Detection

1. Search Perplexity: "n8n CVE-2026-25049"
2. If Perplexity cites our article → tracked
3. Check GA4 for `ai_source: perplexity`

### Console Debugging

All HTML pages now have console.log when AI detected:
```
AI Agent detected: chatgpt
```

Open browser DevTools → Console to see if detection works.

---

## What This Measures

### Success Criteria for AI-First Model

**Week 1 (Feb 14-20):**
- Baseline: How many AI visits do we get currently?
- Target: Any AI visits = proof of concept works

**Week 2-3 (Feb 21-Mar 6):**
- Growth: Are AI visits increasing as we optimize content?
- Target: 5-10 AI visits/week

**Week 4+ (Mar 7+):**
- Validation: Do AI visits correlate with affiliate conversions?
- Target: At least 1 conversion from AI-referred traffic

### Key Questions This Answers

1. **Are AI agents discovering our content?**
   - Yes: See `ai_agent_visit` events
   - No: Schema.org optimization not working, need to iterate

2. **Which AI agent drives most traffic?**
   - Check `ai_source` distribution
   - Focus optimization on top source

3. **Which articles do AI agents cite most?**
   - Check `page_path` parameter
   - Double down on high-performing content types

4. **Does AI traffic convert?**
   - Compare `ai_agent_visit` timestamps with affiliate conversions
   - Calculate conversion rate

---

## Known Limitations

### Detection Gaps

**May not detect:**
- AI agents that don't identify in User-Agent
- New AI tools we haven't added patterns for
- AI agents using proxy/VPN (appear as human traffic)

**False positives:**
- Developers testing with modified User-Agents
- Browser extensions that modify User-Agent

### Crawlers vs Real Visits

**Crawlers (GPTBot, ClaudeBot):**
- Index content for AI knowledge
- Don't click affiliate links
- High volume, low value

**Real visits (ChatGPT-User, Perplexity referrer):**
- AI assisting a human user
- May click affiliate links
- Low volume, high value

**Focus on:** Real visits (chatgpt, claude, perplexity) NOT crawlers.

---

## Next Steps

### Immediate (Today)

1. ✅ Tracking code deployed
2. ⏳ Wait 24 hours for data
3. ⏳ Check GA4 tomorrow (Feb 15) for any `ai_agent_visit` events

### Week 1 (Feb 14-20)

1. Monitor daily for AI visits
2. Test detection with ChatGPT/Claude/Perplexity queries
3. Document which articles get cited
4. Share findings with Delmar/Jeff

### Week 2+ (Feb 21+)

1. Iterate Schema.org markup based on what AI agents prefer
2. Create content types that get cited more
3. A/B test different FAQ formats
4. Track conversion correlation

---

## Accessing Raw Data

### GA4 API Access (for Jim's dashboard)

Event available via GA4 Data API:
- Event name: `ai_agent_visit`
- Custom parameters: `ai_source`, `page_path`

Can export to:
- Google Sheets (automated reporting)
- BigQuery (deep analysis)
- Custom dashboard

### Manual Export

1. GA4 → Reports → Engagement → Events
2. Click `ai_agent_visit`
3. Export icon → Download CSV
4. Contains all parameters + timestamps

---

## Troubleshooting

### "No AI visits showing up"

**Possible causes:**
1. CloudFront cache not invalidated yet (wait 5-10 min)
2. No AI agents have visited yet (need to test manually)
3. AI agents not citing our content yet (Schema.org not working)
4. GA4 processing delay (can take 24-48 hours for reports)

**Check:**
- Real-time view in GA4 (shows immediate events)
- Browser console for "AI Agent detected" message
- View source on live site - tracking code present?

### "Seeing crawler traffic but no real visits"

This is expected initially. Crawlers (GPTBot, ClaudeBot) index constantly. Real visits (ChatGPT-User) only happen when:
1. Human asks AI assistant a question
2. AI searches the web
3. AI finds our content relevant
4. AI cites our article
5. Human clicks through (optional)

**Solution:** Focus on Schema.org optimization to make content more cite-worthy.

---

**Status:** ✅ LIVE as of 09:30 GMT Feb 14, 2026

**Validation:** Check GA4 Real-time tomorrow (Feb 15) for first events.
