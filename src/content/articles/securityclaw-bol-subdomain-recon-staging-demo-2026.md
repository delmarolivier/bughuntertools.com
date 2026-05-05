---
title: "CT Log Recon on bol.com: Two Subdomains, Two Dead Ends, One Useful Map"
description: "SecurityClaw's CT log sweep found hipstershop.stg.bol.com and recruitment-git.bol.com. Neither was exploitable. Here's what we found and why it still mattered."
date: 2026-05-05
category: research
tags: ["bol.com", "subdomain-recon", "certificate-transparency", "bug-bounty", "null-result", "securityclaw"]
---

Not every recon task ends with a finding. Some end with a cleaner map of the target, a better understanding of their infrastructure, and two subdomains that turned out to be exactly what they appeared to be — managed, maintained, and not exploitable.

That's what happened when SecurityClaw swept bol.com's certificate transparency logs and surfaced `hipstershop.stg.bol.com` and `recruitment-git.bol.com`. Both subdomains got full manual investigation. Neither warranted an Intigriti submission. Here's the complete picture of what we found, why each subdomain was worth investigating, and what the null results actually tell us.

## How CT logs surface subdomains

Certificate transparency is a public audit mechanism. Every TLS certificate issued by a trusted CA must be logged in a public CT log before browsers will trust it. That means every subdomain a company has ever obtained a certificate for — staging environments, internal tools, short-lived dev services, deprecated apps — is potentially visible to anyone watching those logs.

For bug hunters, CT logs are a high-signal enumeration source. DNS brute force finds subdomains that match wordlists. CT logs find subdomains that actually exist (or existed). The catch is that "existed" includes decommissioned services where the DNS record persists, the cert was renewed, but the application is gone. You're looking at the full history, not just the current live surface.

SecurityClaw's Campaign 004 ran a CT log sweep against `*.bol.com` as part of ongoing recon on the Intigriti bol.com programme. The two subdomains in this report were among those surfaced. Both had expired certificates in the CT logs, which itself is a signal: expired certs suggest either neglect (possible misconfiguration) or deliberate decommission (probably fine). In both cases, we found recently-renewed active certs when we checked — someone at bol is still managing these.

## Subdomain 1: hipstershop.stg.bol.com

The name is the tell. "Hipster Shop" is Google's [Online Boutique microservices demo application](https://github.com/GoogleCloudPlatform/microservices-demo) — an intentionally feature-rich, intentionally insecure training app. If bol.com had deployed it on a staging subdomain and left it publicly accessible, that's a P1 finding: an exposed staging service with potential test credentials, internal routing, and known vulnerabilities baked into the app by design.

**What we actually found**: DNS resolves to `79.170.100.142` (Google LLC, Utrecht, NL — ASN 396982). TLS certificate is valid (Let's Encrypt, issued 2026-03-05, expires 2026-06-03). HTTP 80 redirects to HTTPS (good hygiene). Then: 404 everywhere.

Peng probed 14 paths — `/`, `/cart`, `/checkout`, `/admin`, `/_ah/health`, `/health`, `/api/currencies`, multiple product paths, `/robots.txt`. All returned HTTP 404 from Google infrastructure. The `via: 1.1 google` response header confirms Google Cloud Load Balancing or Cloud Run — the frontend infrastructure is live, but no application backend is serving traffic behind it.

The assessment: the app was decommissioned while the DNS record and load balancer remained. The cert renewal (2026-03-05 — recent) suggests this is under active management, not forgotten. bol likely shut down the demo after using it for internal testing and left the DNS/infra in place temporarily.

**Why it was worth checking**: If the Hipster Shop app had been live and publicly accessible, the finding would have been significant. The app is designed to be vulnerable — it's a training tool. Deployed on bol's GCP infrastructure in a staging environment, it could have had real credentials injected for test scenarios, real internal network routes, or configuration that bridges staging and production. None of that materialised, but you don't know until you check.

**Verdict**: P3/Informational. Not worth submitting to Intigriti. No data exposed.

## Subdomain 2: recruitment-git.bol.com

The name here is also the tell, in a different direction. "recruitment-git" suggests a Git service — Gitea, GitLab, or similar — used for sharing coding challenge repositories with job candidates. If it existed and had misconfigured access controls, that's a meaningful finding: exposed source code, potential credential leakage, guest access to internal repositories.

**What we actually found**: DNS resolves to `79.170.100.45` (also Google LLC, Utrecht, NL — same /24 range). TLS certificate valid (Let's Encrypt, issued 2026-04-09, expires 2026-07-08 — very fresh). HTTP 200 on `/`. But the response headers tell the real story: `x-guploader-uploadid`, `x-goog-generation`, `x-goog-storage-class: REGIONAL`. This is Google Cloud Storage serving a static file directly, not a web application.

The page content is 269 bytes:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Recruitment coding assignments</title>
</head>
<body>
<h1>Recruitment coding assignments</h1>
<p>You will be given the information on how to get access by your bol recruiter.</p>
</body>
</html>
```

That's the whole page. The GCS bucket backing the domain is not publicly listable — a bucket enumeration attempt returned `NoSuchBucket` (404). Only `/` and `/index.html` return 200. No README, no ZIP files, no `.git`, nothing else accessible without authentication.

The `cache-control: public, max-age=3600` header confirms this is intentionally public. The file upload timestamp — `2026-04-29T06:14:08Z`, the same day Peng ran the investigation — means someone at bol recently updated this page. This is an actively maintained service that intentionally shows candidates a static landing page before routing them to private repositories via their recruiter.

**Why it was worth checking**: The high-value scenario here was a misconfigured Git service with unauthenticated access or a publicly listable GCS bucket containing assignment repos. If candidates could enumerate the bucket and download assignment packages, that's an information disclosure finding — potential source code exposure. The bucket enumeration came back empty. The Git service was never there to begin with.

**Verdict**: P3/Informational. Not worth submitting. Public static page, intentional access, no sensitive data.

## What the null results tell us about bol's infrastructure

Both subdomains share the 79.170.100.x range — Google's regional infrastructure in NL. This is notable: `www.bol.com` is Akamai-fronted and CDN IP blocks are common. These GCP-hosted subdomains (`*.stg.bol.com`, specialty services) are accessible directly from datacenter IPs where the main site might block you.

The infrastructure intelligence is the useful output here. Future campaigns targeting bol.com should consider:

- `*.stg.bol.com` subdomains (staging seller/partner portal, API, shop-API, login) are accessible directly on GCP without CDN interference
- Active cert management suggests these aren't forgotten — someone is maintaining them
- Responsible disclosure: staging environments should be approached carefully. Confirm with the Intigriti programme contact before intensive testing on staging systems

## The discipline of publishing null results

Security research that only publishes P1 findings creates a survivorship bias problem. Bug hunters reading those reports assume the recon that found P1s looked different from the recon that found nothing. It usually didn't. It looked exactly like this: pull CT logs, check each subdomain, document what you find.

The CT log sweep that surfaced `hipstershop.stg.bol.com` and `recruitment-git.bol.com` was the same process that would have found an exposed staging service or a misconfigured Git instance if they'd existed. The process was correct. The target was clean.

Both findings were documented in full, added to the intel DB, and closed as P3/Informational. The infrastructure notes will inform the next campaign. That's how systematic recon is supposed to work.

*Research by Peng — 2026-04-29. Task-71 in the SecurityClaw intel database.*
