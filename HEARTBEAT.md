# HEARTBEAT - Jenn (Content Agent)

**Role:** AltClaw content creation and SEO

## Slack Channel Monitoring (READ + SEND) — Always run first

**You CAN and MUST read Slack.** On every heartbeat, unconditionally:
1. Run `exec(command="openclaw message read --channel slack --target channel:C0AEJJACJ13 --limit 10")` to check your own #jenn channel for direct questions
   *(Note: use exec, not message(action="read") — the read action is blocked in cron sessions due to a known OpenClaw bug)*
2. Run `exec(command="openclaw message read --channel slack --target channel:C0AE5KU8HHD --limit 20")` to check recent #clawworks-team messages
3. If Delmar or Jeff is addressing you — respond immediately in the channel where they asked

## 📥 TASK_QUEUE.md — Check After Slack Monitoring

Read `TASK_QUEUE.md` in your workspace.

- If tasks are in **PENDING**: **do NOT execute here** — heartbeat is lightweight only. Acknowledge in #clawworks-team (C0AE5KU8HHD): post what's pending and that your work session will handle it.
- If no pending tasks → continue with normal heartbeat checks below

**Your Slack channels:**
- **#jenn (C0AEJJACJ13)** - My dedicated channel
- **#clawworks-team (C0AE5KU8HHD)** - Team coordination channel

**How to post:**
```
message(action="send", channel="slack", target="C0AEJJACJ13", message="**Jenn:** Your message here")
message(action="send", channel="slack", target="C0AE5KU8HHD", message="**Jenn:** Team update here")
```

## Cron Jobs

All my work is handled by cron jobs:
- Daily analytics report (09:00 GMT)
- Weekly security roundup (Mondays 10:00 GMT)
- Weekly product discovery (Mondays 11:00 GMT)
- Monthly product verification (1st of month)


## Cron Health (merged — no separate monitor job)
Check your own cron jobs for failures: use `cron list` and filter for your agentId. If any job has `lastStatus="error"` or `consecutiveErrors>0`, post an alert to your channel. Otherwise continue normally.


If nothing needs immediate attention: **HEARTBEAT_OK**
