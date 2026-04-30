---
title: "SecurityClaw Scanned bol.com With 16 AI Skills — Here's What It Found"
description: "Campaign-005 ran SecurityClaw against bol.com on EC2, recovering 2,607 findings including 2,547 expired certs, wildcard issues, and a WAF detection. A look at what the platform revealed."
date: 2026-04-30
category: research
tags: [securityclaw, bug-bounty, bol.com, certificate-hygiene, waf-detection, ec2]
---

> **Affiliate Disclosure:** This site contains affiliate links. We earn a commission when you purchase through our links at no additional cost to you.

SecurityClaw just ran its most complete scan of bol.com yet — and the numbers are stark.

Campaign-005 ran on April 29, 2026, on an EC2 instance with 16 AI-powered security skills executing in parallel. It recovered **2,607 findings** from S3 storage. The previous campaign, run weeks earlier against the same target, returned only 57 findings — not because the platform was cleaner, but because a platform bug was silently truncating output at 24 kilobytes. That issue is now fixed. This is what bol.com actually looks like.

## What SecurityClaw Is

SecurityClaw is an AI-driven security reconnaissance platform built by ClawWorks. It runs structured "campaigns" — target-scoped runs where a set of skills executes concurrently on EC2, each looking for a different class of issue. Skills are stateless Python functions wrapped in a common interface. Results land in S3. A coordinator aggregates them.

Campaign-005 was a validation run: its primary purpose was to confirm that three recent platform fixes actually worked in the field. The target was bol.com — one of the largest e-commerce platforms in Europe, operating a bug bounty program on Intigriti.

## What the Campaign Found

**Certificate hygiene at scale.** The dominant finding was expired TLS certificates: **2,547 expired_cert** findings across bol.com's subdomains. These are certificates that have passed their validity date but are still being served. For a platform at bol.com's scale, this is almost always infrastructure sprawl — decommissioned services, staging environments, and CDN edge nodes that outlive the cert renewal cycle.

These findings are informational at P3 severity. They're not exploitable in the classical sense, but they signal certificate lifecycle management gaps and create risk in environments where clients don't enforce strict cert validation.

**Wildcard certificate exposure.** 53 **wildcard_cert** findings: subdomains serving certificates with `*.bol.com` or similar wildcards. Wildcard certs are a legitimate pattern, but at this count they indicate bol.com relies heavily on wildcard issuance rather than per-service certificates. From a bug bounty perspective, wildcard reuse is worth noting as a scope artifact.

**Unexpected CA.** 6 **unexpected_ca** findings: subdomains presenting certificates issued by a CA outside bol.com's expected trust anchors. The specific subdomain surfaced: `techlab.bol.com`. This is a medium-severity finding (P3 in Intigriti's framework) — it suggests a lab or research environment running with a non-standard PKI setup.

**One WAF block.** A single **WAF_BLOCK** finding: Akamai's WAF returning a 403 on a specific skill's probe. The detection was correct — the skill identified the Akamai response header, extracted the block reason, and logged it with the right payload. This validates the WAF detection skill added in the previous sprint. (There's a minor platform issue to fix: the finding normalizer doesn't yet have a type mapping for `WAF_BLOCK`, so it gets stored under `service_vuln` — that's on the backlog.)

## How the Platform Validated Its Own Fixes

Campaign-005 was explicitly designed to confirm three prior fixes:

**S3 results pipeline (PR #910):** The previous campaign lost ~2,550 findings to SSM stdout truncation. The fix reroutes results to S3 — large outputs go directly to bucket storage, bypassing the 24KB SSM cap entirely. Campaign-005 returned 978,146 bytes of findings with no truncation. Fix confirmed.

**Context-optional skills (PR #911):** 16 of 16 skills ran successfully with zero context-related failures. The fix decoupled skills from a required context parameter that was causing silent failure when context wasn't provided. Fix confirmed across the full skill set.

**WAF detection (PR #914):** The WAF skill correctly identified the Akamai 403, extracted the right payload, and generated a finding. Partial confirmation — the detection works, but the output normalizer needs a follow-up fix to map `WAF_BLOCK` to its own finding type instead of falling through to `service_vuln`.

**Bonus fix discovered.** While validating, the team found a dead code path that had been hiding in `run_campaign.py` since the S3 collection was first written: the `s3_client` object was created but never passed to the execution function, meaning S3 collection was silently skipped on every run. It was fixed in this PR.

## What This Looks Like in Practice

Campaign-005 ran in **4 minutes 8 seconds** on a single EC2 instance. 16 skills. 2,607 findings. No truncation, no context failures. If you're benchmarking what automated security reconnaissance against a major European e-commerce platform looks like in 2026, that's the number.

The cert hygiene findings won't produce bounty payouts — they're informational — but they're exactly the kind of surface that informs a more targeted follow-up campaign. Where are the unexpired but misissued certs? What's `techlab.bol.com` running under that unexpected CA? What does the WAF's fingerprint reveal about which resources it's protecting?

Campaign-006 is scoped to dig into those questions. The platform is ready.
