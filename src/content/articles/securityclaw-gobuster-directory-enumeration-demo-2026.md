---
title: "We Hid 10 Secrets on a Web Server. SecurityClaw Found All 10 in Under 5 Seconds."
description: "We planted 10 sensitive paths on a web server — backup files, Git repo, live API keys, admin panel. SecurityClaw's gobuster integration found all 10 in 4.79 seconds. Here's exactly how."
date: 2026-05-02
category: research
tags: [gobuster, directory-enumeration, web-scanning, securityclaw, penetration-testing]
---

> **Affiliate Disclosure:** This site contains affiliate links. We earn a commission when you purchase through our links at no additional cost to you.

**`/backup.zip` and `/config.bak` were on the same server. The backup contained the database. The config file contained the password. An attacker who ran our scan had both in their hands within 2.56 seconds of starting.**

That's the story of SecurityClaw Campaign D12. We built a fake corporate web server, hid 10 sensitive paths across it, and pointed gobuster at the root. What follows is exactly what it found — and the one technique gap that matters more than the tool.

---

## The Setup

The target was `AcmeCorp Portal` running on localhost:19090. Clean homepage: `/`, `/about`, `/contact`, `/robots.txt`. Nothing suspicious. The robots.txt deliberately omitted all sensitive paths — the kind of defence developers add and attackers expect and ignore.

Hidden across the server were 10 planted paths:

| Path | What It Exposes | Severity |
|------|----------------|----------|
| `/.git/HEAD` | Git repo exposure — source code recovery possible | HIGH |
| `/admin/` | Admin panel, no authentication | HIGH |
| `/admin/login` | Login form, no rate limiting | MEDIUM |
| `/admin/dashboard` | Business metrics: 1,247 users, $84,320 revenue | HIGH |
| `/backup.zip` | Database backup archive | **CRITICAL** |
| `/config.bak` | DB credentials in plaintext (`pass=Sup3rS3cr3t!`) | **CRITICAL** |
| `/phpinfo.php` | PHP 7.4.33 (EOL Nov 2022) + server internals | MEDIUM |
| `/wp-admin/` | WordPress admin login | MEDIUM |
| `/api/v1/users` | Unauthenticated user enumeration | HIGH |
| `/api/v1/keys` | Live production Stripe `sk_live_*` API keys | **CRITICAL** |

Three CRITICAL findings. Four HIGH. The question wasn't whether gobuster would find them — the question was whether the technique was right.

---

## What SecurityClaw Found

SecurityClaw ran gobuster in two passes. This is the honest version of how directory enumeration actually works.

**Scan 1 — `dirb/common.txt` with extension fuzzing (2.56s):**

```
/.git/HEAD            (Status: 200) [Size: 21]
/admin                (Status: 301) [Size: 0] [--> /admin/]
/api                  (Status: 200) [Size: 61]
/backup.zip           (Status: 200) [Size: 100]
/config.bak           (Status: 200) [Size: 57]
/phpinfo.php          (Status: 200) [Size: 118]
/robots.txt           (Status: 200) [Size: 34]
/wp-admin             (Status: 301) [Size: 0] [--> /wp-admin/]
```

**Scan 2 — Recursive follow on `/admin/` (2.23s):**

```
/dashboard            (Status: 200) [Size: 88]
/login                (Status: 200) [Size: 131]
```

**Result: 10/10. 4.79 seconds total. Zero false positives.**

The command:

```bash
gobuster dir \
  -u http://target/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,zip,bak,txt,html,git \
  -t 20 -q
```

---

## Why the Three CRITICAL Findings Are Actually One Attack

These three findings don't sit in isolation — they form a complete kill chain:

**`/backup.zip` + `/config.bak` = instant database compromise**

`config.bak` contained: `host=db.internal`, `user=admin`, `pass=Sup3rS3cr3t!`. The backup archive almost certainly contains the database itself. An attacker with both files has credentials to exfiltrate the entire database without touching the application layer. No SQL injection required. No brute forcing. Download two files and you're done.

**`/api/v1/keys` = every third-party integration fully compromised**

Live `sk_live_*` Stripe keys served with zero authentication. Every API integration built on these keys — payment processing, subscription management, webhooks — is now under attacker control.

**`/.git/HEAD` = source code and secrets in commit history**

A live `.git/HEAD` response means the full `.git/` directory is exposed. git-dumper can recover the entire commit history in minutes. Developers who deleted secrets from git history — thinking they were safe — find out they weren't. (We covered that exact scenario in [our Gitleaks article](/articles/securityclaw-gitleaks-git-history-secret-detection-demo-2026/).)

---

## The Honest Gap: It's Not the Tool, It's the Technique

Here's what the raw `gobuster dir` run *without* the right technique would have missed:

**1. Extension fuzzing is not optional.** Without `-x php,zip,bak,txt,html,git`, gobuster would never find `backup.zip` or `config.bak`. The wordlist contains directory and page names — it doesn't guess file extensions unless you tell it to. These two CRITICAL files are invisible without `-x`.

**2. Recursive scanning is a second step, not a feature.** `/admin` returned a 301 redirect. Gobuster records the redirect — it does not automatically enumerate `/admin/` sub-paths. The admin dashboard and login form were only found because SecurityClaw scheduled a second targeted scan after identifying the redirect in scan 1. One pass is not enough.

**3. Deep API paths need dedicated wordlists.** `common.txt` found `/api` — the root endpoint — because it disclosed its sub-paths in a JSON response. `/api/v1/users` and `/api/v1/keys` were found via that JSON, not via wordlist match. For API-heavy targets, a specialised API paths wordlist (or a manual follow-up on every `/api` endpoint) is required.

**4. `.git/config` is not the same as `.git/HEAD`.** `common.txt` contains `.git/HEAD`. Full git repo recovery requires `.git/config` and additional refs — a specialised git wordlist or git-dumper is the right tool to confirm source code exfiltration is possible.

This is exactly the SecurityClaw product story: gobuster is fast but dumb by design. It walks a list. The intelligence is in wordlist selection, extension configuration, redirect handling, and recursive scheduling — the campaign orchestration layer that SecurityClaw builds on top.

---

## Key Stats

| Metric | Value |
|--------|-------|
| Tool | gobuster v3.8 |
| Wordlist | dirb/common.txt (~4,600 entries) |
| Extensions tested | php, zip, bak, txt, html, git |
| Threads | 20 |
| Planted paths | 10 |
| Found | **10/10 (100%)** |
| Total scan time | **4.79 seconds** |
| Critical findings | 3 |
| High findings | 4 |
| False positives | 0 |
| Campaign result | **PASS** |

---

## What This Means for Defenders

If you're running a web application, three questions:

1. **Do you have backup files accessible from the web root?** `.zip`, `.bak`, `.sql`, `.tar.gz` — any file a developer created for convenience and forgot to remove. Run gobuster with extension fuzzing on your own server before someone else does.

2. **Is your `.git` directory exposed?** Check `/.git/HEAD` on your production domain right now. If you get a 200 with content, you have a source code exposure problem. The fix is one nginx `deny` directive or `.htaccess` rule.

3. **Are your admin paths guessable?** `/admin`, `/wp-admin`, `/dashboard`, `/panel` are in every wordlist. Authentication is not an excuse — unauthenticated admin panels are an immediate CRITICAL; authenticated admin panels with guessable paths are an information disclosure and brute-force surface.

---

## For Bug Bounty Researchers

Directory enumeration is minute 2 of every web pentest for a reason. The typical bug bounty workflow:

1. Run gobuster with `common.txt` + extension fuzzing as your first pass
2. Note every 301 redirect — schedule a recursive follow on each one
3. Check every `.git/HEAD` hit with git-dumper to confirm repo exposure
4. For API endpoints discovered in JSON responses, pivot to a dedicated API paths list
5. Correlate backup/config file hits — they're almost always related to each other and to the database

The backup + config combination is underrated. Bug bounty programs that pay critical for SQLi pay the same or more for direct database credential exposure. It's faster to find, requires no exploitation, and produces a concrete credential to prove impact.

---

## SecurityClaw Campaign D12 — Dual Scanner Pairing

For secret detection alongside directory enumeration, SecurityClaw pairs gobuster with TruffleHog v3 and Gitleaks. Once a `.git` directory is confirmed exposed:

- **Gitleaks** scans the repository history for secrets committed and later deleted — see [the Gitleaks demo](/articles/securityclaw-gitleaks-git-history-secret-detection-demo-2026/) for how a deleted RSA key was found in 13.2ms
- **TruffleHog v3** live-verifies whether discovered credentials are still active

Finding the path is step one. Confirming whether the credentials work — and whether deleted secrets are still exposed — is the full picture.

---

*Campaign D12 data provided by Peng. All tests conducted in a controlled environment on a locally hosted demonstration target. No live production systems were accessed.*
