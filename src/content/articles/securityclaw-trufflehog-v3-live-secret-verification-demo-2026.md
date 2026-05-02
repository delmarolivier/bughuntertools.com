---
title: "It Doesn't Just Find Your Leaked Secrets — It Tells You If They Still Work"
description: "SecurityClaw ran TruffleHog v3.95.2 against a controlled repo with 5 planted secrets. All 5 detected — including the Stripe key v2 missed. The real story: live verification tells you instantly if a leaked credential is still active."
date: 2026-05-02
category: research
tags: [trufflehog, secrets-detection, git-security, credential-scanning, securityclaw]
---

When a secret leaks into a git repo, two questions matter immediately: *did the scanner catch it*, and *is it still active*?

TruffleHog v2 answered the first question most of the time. TruffleHog v3 answers both — in a single scan.

SecurityClaw ran v3.95.2 against a controlled canary repo with five intentionally planted secrets. All five were detected. Then, for each finding, TruffleHog called the real API to check if the credential was still valid. The result state — `verified`, `unverified`, or `filtered_unverified` — tells you exactly how bad the situation is before you've opened a single incident ticket.

## The Setup

Three files, three commits, five secrets:

- `config.py` — AWS Access Key + AWS Secret Access Key
- `deploy.sh` — GitHub Personal Access Token + Slack Webhook URL
- `payment.js` — Stripe live key (`sk_live_`)

The secrets are canary values — fake keys with real patterns. The goal is to test detection and verification behaviour without exposing real credentials.

Command run on securityclaw-kali:

```bash
trufflehog git file:///path/to/repo \
  --json --no-update \
  --results=verified,unverified,unknown,filtered_unverified
```

Scan time: **~460ms** for three commits.

## The Results

| Secret | File | Detected? | v3 State |
|---|---|---|---|
| AWS Access Key + Secret | config.py | ✅ YES | `filtered_unverified` |
| GitHub PAT | deploy.sh | ✅ YES | `filtered_unverified` |
| Slack Webhook | deploy.sh | ✅ YES | `unverified` |
| Stripe live key | payment.js | ✅ YES | `filtered_unverified` |

**Detection rate: 5/5 (100%).** False positives: 0.

## The v2 Comparison

TruffleHog v2 (Python) missed the Stripe `sk_live_` key entirely. The Stripe pattern wasn't in the v2 ruleset — a known gap, documented at the time. The fix came with the v3 Go rewrite: dedicated detectors for AWS, GitHub, Slack, Stripe, and hundreds of other services.

Running the same canary repo through v2 returned four findings. v3 returns five.

## What the Result States Actually Mean

This is where v3 changes the incident response calculus.

When TruffleHog finds a secret, it tries to verify it by calling the real API with the credential:

| State | What happened | What to do |
|---|---|---|
| `verified` | Secret found. API confirmed it's **still active**. | Rotate immediately. |
| `unverified` | Secret found. No API available to verify (e.g., Slack webhooks don't expose a check endpoint). | Treat as real — assume it works. |
| `unknown` | Verification attempted. API returned an error. | Could be valid, could be a transient error. Rotate to be safe. |
| `filtered_unverified` | Secret found. API says it doesn't exist (invalid/expired/fake key). | Detected but dead — canary keys and already-rotated secrets land here. |

In a real repo with a live Stripe key, that finding shows up as `verified`. You don't need to manually check whether the key still works — TruffleHog already did.

## Why Canary Keys Show as `filtered_unverified`

Our demo secrets are fake values — `AKIAIOSFODNN7EXAMPLE` and `sk_live_51ABCDEF...dc` are example patterns that don't exist in AWS or Stripe's systems. v3 detects them via pattern matching, calls the API, gets rejected, and marks them `filtered_unverified`.

By default, running TruffleHog without the `--results=filtered_unverified` flag only shows `verified`, `unverified`, and `unknown` findings — which reduces noise for production use. The full flag is needed to see canary/expired keys.

For real-world scanning, the default output is exactly what you want: only findings that are real secrets, either confirmed active or unverifiable.

## The JSON Output

What TruffleHog v3 actually returns for the Stripe finding:

```json
{
  "SourceMetadata": {
    "Data": {
      "Git": {
        "commit": "da554db75f5ef4048f0cf12ec6c7dd97ce3594ec",
        "file": "payment.js",
        "timestamp": "2026-05-02 00:46:13 +0000",
        "line": 3
      }
    }
  },
  "DetectorName": "Stripe",
  "DetectorDescription": "Stripe is a payment processing platform...",
  "Verified": false,
  "Raw": "sk_live_51ABCDEF...<redacted>...dc",
  "ExtraData": {
    "rotation_guide": "https://howtorotate.com/docs/tutorials/stripe/"
  }
}
```

Notice the `rotation_guide` field. TruffleHog v3 includes direct links to rotation documentation for each secret type. When a finding hits `verified`, the path from "we found it" to "we rotated it" is one click.

## The AWS Finding — Paired Key Detection

The AWS Access Key and Secret Access Key were detected as a single finding, with both values in the output:

```json
{
  "DetectorName": "AWS",
  "Verified": false,
  "Raw": "AKIAIOSFODNN7EXAMPLE",
  "RawV2": "AKIAIOSFODNN7EXAMPLE:wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "ExtraData": {
    "resource_type": "Access key"
  }
}
```

The `RawV2` field contains the key+secret pair. AWS requires both to make API calls, so detecting the pair in one finding is operationally cleaner than two separate alerts.

## Pairing with Gitleaks

TruffleHog v3 and Gitleaks solve overlapping but distinct problems. TruffleHog's live verification is unique — Gitleaks doesn't call the API. But Gitleaks' entropy analysis catches secrets that don't match known patterns — high-entropy strings that might be custom API keys or internally generated tokens.

In SecurityClaw's scanning approach, we run both. [SecurityClaw's Gitleaks demo](/articles/securityclaw-gitleaks-git-history-secret-detection-demo-2026/) covers the entropy detection angle — including how Gitleaks found an RSA private key three commits after it was "deleted" from the repo. TruffleHog catches the known patterns and tells you if they're active. Gitleaks catches what patterns miss.

Running one without the other leaves gaps.

## What This Catches in Practice

The secrets detected in this demo are the five most commonly leaked credential types we see in real repos:

- **AWS credentials** — accidentally committed from `.env` files or CI config
- **GitHub tokens** — from developer scripts that were never meant to be committed
- **Slack webhooks** — from integration setups pasted directly into code
- **Stripe live keys** — from developers testing payment flows locally with real credentials

None of these are exotic. They show up in repos of every size, in companies of every maturity level. The pattern is always the same: someone commits a secret, it gets pushed, it lives in git history forever — even after the file is removed.

TruffleHog v3 scans the full history, not just the current state of the repo. Every commit, every branch, every file that ever existed.

## The Takeaway

v3 does two things v2 didn't:

1. **It catches the Stripe key.** The 20% gap from v2 is closed. 100% detection on the five most common secret types.
2. **It tells you if the secret still works.** `verified` means rotate now. `unverified` means treat it as real. The difference between a minor cleanup task and a P1 incident is visible immediately in the scan output.

SecurityClaw integrates TruffleHog v3 as a standard scan. One command, full git history, live verification on every finding.
