# HEARTBEAT - Jenn (Content Agent)

**Role:** AltClaw content creation and SEO

## 📥 TASK_QUEUE.md — Check First on Every Heartbeat

**Before anything else:** Read `TASK_QUEUE.md` in your workspace.

- If tasks are in **PENDING**: immediately update the file to mark them **IN PROGRESS**, then do the work
- When work is complete: update the file to mark **DONE** with a brief completion note
- If no pending tasks → continue with normal heartbeat checks below


## Slack Channel Monitoring (READ + SEND)

**You CAN and MUST read Slack.** On every heartbeat:
1. Run `exec(command="openclaw message read --channel slack --target channel:C0AE5KU8HHD --limit 10")` to check recent #clawworks-team messages
   *(Note: use exec, not message(action="read") — the read action is blocked in cron sessions due to a known OpenClaw bug)*
2. If Delmar or Jeff is addressing you — respond immediately in #clawworks-team (C0AE5KU8HHD)
3. Then continue with your normal checks below

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
