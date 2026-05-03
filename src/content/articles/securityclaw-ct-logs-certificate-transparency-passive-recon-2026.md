---
title: "Before You Send a Single Packet: How CT Logs Mapped 79 Superdrug Subdomains in 12 Seconds"
description: "Certificate Transparency logs expose every SSL certificate ever issued — and 12+ years of your infrastructure history. SecurityClaw found 79 subdomains on a live bug bounty target before sending a single packet."
date: 2026-05-03
category: research
tags: [passive-recon, certificate-transparency, subdomain-enumeration, bug-bounty, securityclaw]
---

Before a penetration tester sends a single packet to the target, the internet has already told them everything they need to know.

Every SSL/TLS certificate ever issued for a domain is logged in a public, searchable database called Certificate Transparency. CISA mandated it. Browsers enforce it. And it means that years of a company's infrastructure history — staging servers, abandoned subdomains, UAT environments, vendor relationships — is sitting in a public log anyone can query.

We ran SecurityClaw's ct-logs skill against `superdrug.com`, an authorized [Intigriti](https://intigriti.com) bug bounty target. In **12.57 seconds**, with **zero requests sent to the target**, we discovered **79 unique subdomains** and **12+ years of infrastructure intelligence**.

---

## What Is Certificate Transparency?

When a Certificate Authority (CA) issues an SSL/TLS certificate, it's required to submit that certificate to one or more publicly auditable CT logs. This was introduced to catch mis-issued certificates — but it has a side effect: every domain name and subdomain in every certificate becomes permanently searchable.

The key point is that this is **mandatory and irreversible**. You cannot opt out of CT logging and still have your site work in modern browsers. Everything that's had a certificate issued since 2013 (and some earlier via backdated logging) is in there.

SecurityClaw queries [crt.sh](https://crt.sh), a free PostgreSQL-backed CT log aggregator, to pull this data. The command is one line:

```bash
# Discover subdomains passively — zero noise
python3 ct_search.py superdrug.com --output subdomains

# Full intelligence report: CAs, dates, SANs
python3 ct_search.py superdrug.com

# Pipe discovered subdomains directly into nuclei
python3 ct_search.py example.com --output subdomains | \
  nuclei -l - -t exposures/
```

No authentication required. No rate limits worth worrying about. No alerts triggered on the target.

---

## The Numbers

| Metric | Result |
|---|---|
| Certificates found | **1,499** |
| Unique subdomains | **79** |
| Infrastructure history | **12+ years (2009–2026)** |
| CA issuers identified | **15+** |
| Scan time | **12.57 seconds** |
| Packets sent to target | **0** |

---

## What We Actually Found

### Staging and UAT — The Full Environment Ladder

CT logs handed us Superdrug's entire environment naming convention before we touched a single host:

- `hyve-staging.superdrug.com` — staging server on Hyve hosting (2017–2018)
- `pharmacy-uat.superdrug.com` / `www.pharmacy-uat.superdrug.com` — pharmacy UAT
- `www-etst.superdrug.com`, `www-euat.superdrug.com`, `www-pre.superdrug.com`, `www-tst.superdrug.com`, `www-uat.superdrug.com`, `www-prd.superdrug.com` — the complete environment ladder from test to production
- `uat-appcms.superdrug.com`, `pre-appcms.superdrug.com` — CMS staging environments

Why does this matter? UAT and staging environments frequently have weaker security controls than production. They may not be behind the same WAF. Authentication is often relaxed. Now we know they exist — and the naming convention tells us exactly where to look for others we haven't seen yet.

### Active Services

- `onlinepharmacy.superdrug.com` — the NHS pharmacy platform (this became our primary F1 submission target)
- `preview.onlinepharmacy.superdrug.com` — preview environment
- `onlinedoctor.superdrug.com` — online doctor service, certificates dating to 2013
- `healthclinics.superdrug.com` with wildcard `*.healthclinics.superdrug.com` — health clinics
- `dare.superdrug.com` / `dareapp.superdrug.com` — the DARE health app
- `appcms.superdrug.com` — app content management system
- `opticians.superdrug.com`, `support.opticians.superdrug.com` — optical services
- `thehub.superdrug.com` — internal hub (historical, now offline — but documented in the logs)
- `email.superdrug.com` — email infrastructure

The value here isn't just the list. It's that historical certificates show when services came online, which tells you about technology choices and migration patterns. `onlinedoctor.superdrug.com` has been running since 2013. That's 13 years of potential accumulated technical debt.

### Third-Party Vendor Relationships Exposed via SANs

This is where CT logs get genuinely interesting for an attacker.

When a CA issues a certificate, it can bundle multiple domain names together in the Subject Alternative Names (SAN) field. Those bundles sometimes reveal vendor relationships the target never intended to make public.

**The Pugpig find:** `dareapp.superdrug.com` appeared in the same certificate as `www.pugpig.com` in 2017–2018. That single certificate tells us: **Pugpig** is (or was) Superdrug's mobile app publishing platform. Now a pentester knows which third-party ecosystem to investigate — and Pugpig's infrastructure may be in scope depending on the program rules.

**The AS Watson confirmation:** Multiple certificates bundled `aswatson.eu` alongside `www.superdrug.com`, confirming the parent company relationship and which shared infrastructure exists.

### The CA Issuer Surprise

The CA breakdown is intelligence in its own right:

| CA | Cert Count | What It Suggests |
|---|---|---|
| GlobalSign CloudSSL | 444 | Historical CDN / shared hosting |
| Let's Encrypt R3 | 208 | Automated DevOps pipelines |
| Amazon RSA (M01–M04) | 110+ | CloudFront / ACM distributions |
| **cPanel CA** | **76** | **⚠️ Shared hosting** |
| GeoTrust RSA | 62 | Enterprise DigiCert contracts |
| Cloudflare | 27+ | CDN-proxied services |
| Google Trust Services | 25+ | Firebase / GCP services |

The cPanel finding stood out. cPanel is primarily a shared hosting control panel — it's not what you'd expect from a major UK retailer's infrastructure. 76 certificates issued by cPanel's CA suggests something in Superdrug's stack uses shared hosting with another tenant. For an attacker, shared hosting is a priority target: cross-tenant vulnerabilities, misconfigurations, and privilege escalation scenarios all become relevant.

---

## Honest Assessment: What CT Logs Miss

We document gaps honestly. CT logs are powerful but not complete:

**What they miss:**
- HTTP-only services (no certificate = invisible to CT logs)
- Very new domains (CT log propagation takes minutes to hours after issuance)
- Internal / private PKI subdomains (self-signed or private CA certs aren't submitted to public logs)
- DNS-only subdomains without any certificate

**Our gap estimate:** For a security-conscious retailer like Superdrug, we'd expect to miss roughly 10–15% of total subdomains via CT logs alone. Almost everything they expose publicly should have TLS. The gap is internal tooling and services that never needed a public cert.

The fix: follow CT log recon with DNS brute-force and active crawling. CT logs don't replace those techniques — they front-load the intelligence so you're not going in blind.

---

## Why CT Logs Should Be Step 1 of Every Assessment

Active scanners are loud. Nmap sends packets. Nikto generates HTTP requests. WAFs log them, rate-limit them, block them. A sufficiently aggressive scan can trigger alerts before you've even understood the attack surface.

CT logs generate zero noise on the target. No HTTP requests. No WAF interactions. No rate limits. Just a query to a public database that exists independently of the target's infrastructure.

What you get back in 12.57 seconds:

1. **Complete subdomain list** — every domain that's ever had a cert
2. **Historical timeline** — when services came online, when they were decommissioned
3. **Environment intelligence** — naming conventions for staging, UAT, prod
4. **Vendor relationships** — third parties embedded in the target's certificate history
5. **Infrastructure diversity** — which cloud, CDN, and hosting providers are in use

Our authorized bug bounty recon on `onlinepharmacy.superdrug.com` eventually took us weeks to fully map. CT logs would have shown the pharmacy platform on day one — before we'd sent a single packet.

---

## Connecting the Dots: CT Logs → Active Scanning

The output of CT log recon feeds directly into active tools. SecurityClaw is designed for this pipeline:

```bash
# Step 1: CT logs — passive, zero noise
python3 ct_search.py superdrug.com --output subdomains > targets.txt

# Step 2: Nuclei — scan discovered subdomains for misconfigurations
nuclei -l targets.txt -t exposures/ -t misconfiguration/

# Step 3: Gobuster — directory enumeration on interesting subdomains
gobuster dir -u https://target.superdrug.com -w /usr/share/wordlists/dirbuster/medium.txt
```

The [Nuclei demo article](/articles/securityclaw-nuclei-misconfiguration-scanner-demo-2026/) covers what happens when you feed a subdomain list into the misconfiguration scanner: AWS credentials exposed in 8 seconds, 23 findings across 83% of targets.

That pipeline — CT logs first, active scanners second — is how SecurityClaw structures a real assessment. Start with what the internet has already given you. Then get loud.

---

## The Takeaway for Defenders

If you run infrastructure under a domain, check what CT logs expose about you. The tools are free:

- [crt.sh](https://crt.sh) — search your domain, browse all historical certs
- [Google's CT Dashboard](https://transparencyreport.google.com/https/certificates) — monitor new certs being issued

What to look for: staging subdomains that shouldn't be public, old certs for services you thought were decommissioned, unexpected third-party domain bundling. If you find subdomains you don't recognise, investigate before an attacker does.

The CT log database is public, permanent, and growing. The question isn't whether attackers are querying it for your domain. The question is whether you are.

---

*SecurityClaw's ct-logs skill queries [crt.sh](https://crt.sh) against authorized bug bounty targets on the Intigriti platform. Demo target: `superdrug.com`. Campaign ID: 17.*
