# TASK_QUEUE.md

**Check this file on every heartbeat.** If there are PENDING tasks, act on them.

---

## 📥 PENDING

### Content Pipeline — SEO Article Queue (from Bob's keyword research)
- **From:** Bob (Marketing)
- **Added:** 2026-02-20 14:12 GMT
- **Priority:** NORMAL
- **Status:** PENDING

Three article opportunities handed off by Bob following SEO keyword research (file: `seo-keyword-research-2026-02-20.md` in Bob's workspace):

1. "Why Your Security Scanner Isn't a Penetration Test" — top-funnel educational, keywords: automated vulnerability scanner, penetration testing, DAST vs pentesting
2. "The Complete Guide to Automated Penetration Testing in 2026" — pillar content, 2,000+ words, keywords: automated pentesting, AI pentesting tool, autonomous penetration testing
3. "Burp Suite Costs $450/yr Per User — What Teams Actually Spend" — high commercial intent, keywords: burp suite alternative, burp suite pricing

Hold: SecurityClaw vs Penligent comparison — waiting on Peng's tech diff (now sent to Bob, unblocked).
Awaiting Bob's response on outline-first vs full draft approach before starting #1.

---

## 🔄 IN PROGRESS

*(none)*

---

## ✅ DONE

### Daily Standup — Fri Feb 20 2026
- **From:** Jeff
- **Added:** 2026-02-20 09:07 GMT
- **Priority:** HIGH
- **Status:** DONE

[DONE] Completed 2026-02-20 09:12 GMT — Posted Friday standup to #clawworks-team. Noted analytics cron error (likely missing_scope delivery issue, not content failure).

---

### Seed & Maintain GitHub Project Board
- **From:** Jeff (CTO)
- **Added:** 2026-02-19 18:41 GMT
- **Priority:** HIGH
- **Status:** DONE

[DONE] Completed 2026-02-19 19:24 GMT — Seeded GitHub Project Board #4 (AltClaw Content Strategy) with 5 draft items: Daily Analytics Report, Weekly Security Roundup, Weekly Product Discovery Report, Monthly Product Verification & Content Audit, SEO Content Strategy. All set to Todo status.

---

## 📋 How tasks work

Jeff or other agents write tasks here. You process them on heartbeat.

**When you pick up a task:** move it from `PENDING` → `IN PROGRESS` and update the file immediately.
**When you finish:** move it from `IN PROGRESS` → `DONE` and add a completion note.

### Task format:
```
### Task Name
- **From:** Jeff
- **Added:** YYYY-MM-DD HH:MM GMT
- **Priority:** HIGH / NORMAL / LOW
- **Status:** PENDING → IN PROGRESS → DONE

Task description and context here.

[DONE] Completed YYYY-MM-DD HH:MM GMT — brief note on what was done.
```

---

### Test Slack chat:write OAuth Fix
- **From:** Delmar
- **Added:** 2026-02-20 14:13 GMT
- **Priority:** HIGH
- **Status:** DONE

[DONE] Completed 2026-02-20 14:14 GMT — Posted test message to #clawworks-team, confirmed `chat:write` scope working.


---

### ⚠️ Cross-Agent Requests (Updated 2026-02-20)

If you need another agent to do something:
1. **Write a request to Jeff's TASK_QUEUE.md** (`/home/delmar/.openclaw/workspace/TASK_QUEUE.md`) under `📥 INBOUND REQUESTS`
2. **Also post to #clawworks-team** so the team has visibility
3. Jeff reviews, approves, and routes to the target agent

**Do NOT write directly to other agents' TASK_QUEUE.md files.** All allocation goes through Jeff.

---

### GSC Sitemap Submitted — Log and Monitor
- **From:** Jeff / Delmar
- **Added:** 2026-02-20 17:35 GMT
- **Priority:** MEDIUM
- **Status:** DONE

[DONE] Completed 2026-02-20 17:42 GMT — Logged milestone, acknowledged in #clawworks-team. Sitemap https://bughuntertools.com/sitemap.xml submitted by Delmar. 13 articles live. Monitoring for first impressions data (expected 3–7 days) — daily analytics cron will pick this up.


---

### Confirm node_modules Cleanup
- **From:** Delmar / John
- **Added:** 2026-02-20 18:58 GMT
- **Priority:** MEDIUM
- **Status:** DONE

[DONE] Completed 2026-02-20 19:12 GMT — Confirmed safe (duplicate of earlier 08:42 confirmation). Eleventy build dep, recoverable via `npm install`. John cleared to proceed.
