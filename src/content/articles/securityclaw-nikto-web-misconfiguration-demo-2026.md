---
title: "17 Findings in 4 Seconds: SecurityClaw's Web Scanner Finds Everything We Hid"
description: "SecurityClaw ran Nikto against a server we deliberately misconfigured. 5/5 planted misconfigs found in 4 seconds — plus 12 real issues we hadn't even planted. Including the one that hands attackers your entire codebase."
date: 2026-05-03
category: research
tags: [nikto, web-security, misconfiguration, git-exposure, securityclaw]
---

We set up a web server with five deliberate security problems. Backup archives. Debug files in production. An exposed Git repository. Apache internals. Credentials in plaintext. Then we pointed SecurityClaw at it.

Nikto v2.5.0 found all five in four seconds — plus twelve more real issues we hadn't planted.

Here's what it found, how it found it, and why the Git exposure is the one that should worry you most.

---

## The Setup

Controlled Python SimpleHTTP server on `localhost:18080`. Five misconfigurations planted intentionally:

1. **backup.zip** — a backup archive left accessible over HTTP (CWE-530)
2. **test.php** — a debug/test file left in production (RCE potential if PHP were executing)
3. **.git/HEAD** — the Git repository exposed via HTTP (source code fully extractable)
4. **/server-status** — Apache internals endpoint accessible from the outside
5. **readme.txt** — version info and credentials accessible in plaintext

Scan command: `nikto -h http://localhost:18080 -nointeractive -maxtime 60s`

---

## The Results

| Finding | Severity | Planted? | Found? |
|---|---|---|---|
| backup.zip accessible | MEDIUM | ✅ Yes | ✅ YES |
| test.php in production | MEDIUM | ✅ Yes | ✅ YES |
| .git/HEAD exposed | HIGH | ✅ Yes | ✅ YES |
| /server-status accessible | MEDIUM | ✅ Yes | ✅ YES |
| readme.txt accessible | LOW | ✅ Yes | ✅ YES |
| Missing X-Frame-Options | MEDIUM | No | ✅ Real |
| Missing X-Content-Type-Options | MEDIUM | No | ✅ Real |
| 10 additional real issues | Various | No | ✅ Real |
| Weblogic /%2e/ probe | — | No | ⚠️ FP |
| PHP info disclosure probe | — | No | ⚠️ FP |

**Detection rate: 5/5 planted (100%)**
**Total findings: 17** — 5 planted + 12 real issues identified as a bonus
**False positives: 2** (documented, expected — more on this below)
**Scan time: 4 seconds**

---

## The Finding That Matters Most: .git/HEAD

When Nikto flags `.git/HEAD` accessible over HTTP, the severity is hard to overstate.

Git stores its entire object database in the `.git/` directory. If that directory is served by your web server — which happens far more often than anyone admits, typically when developers `git clone` a project directly into the web root — an attacker doesn't need any exploit. They just need an HTTP client and a tool like [git-dumper](https://github.com/arthaud/git-dumper) or GitTools.

The reconstruction works like this: Nikto fetches `.git/HEAD` and finds a branch reference (e.g. `ref: refs/heads/main`). From there, the attacker can enumerate object hashes, download pack files, and reconstruct the entire working tree. That includes:

- **API keys and secrets** committed before someone remembered to add `.env` to `.gitignore`
- **Database credentials** in config files
- **Deployment scripts** with SSH keys or cloud provider tokens
- **Entire commit history** — including secrets that were "deleted" in a later commit (deletion doesn't rewrite history)

This is why SecurityClaw treats `.git/HEAD` exposure as a HIGH severity finding, not medium. The file itself is harmless. What it unlocks is not.

The fix is two lines in your nginx or Apache config:

```nginx
location ~ /\.git {
    deny all;
}
```

Or for Apache:
```apacheconf
<DirectoryMatch "\.git">
    Require all denied
</DirectoryMatch>
```

Check your staging environments. Developers spin these up quickly, sometimes directly from a `git clone`. The production config often has the right rules; the staging server that got set up in fifteen minutes may not.

---

## The Other Four: Faster to Fix, Still Real

**backup.zip** — Backups created in the web root are accessible to anyone who guesses the filename. Common names: `backup.zip`, `backup.tar.gz`, `site-backup-2024-01-15.zip`. Nikto has a wordlist of these. The contents typically include: the entire site source, database dumps, and `.env` files. Move backups out of the web root or use object storage with no public access.

**test.php** — Debug and test files are the bread and butter of web misconfig scanning. `test.php`, `phpinfo.php`, `debug.php`, `info.php` — Nikto checks for all of them. In this demo the server wasn't running PHP so the RCE risk was theoretical, but in production these files frequently execute. A `phpinfo()` output alone leaks server version, PHP configuration, extension list, loaded modules, and environment variables — a reconnaissance goldmine.

**/server-status** — Apache's `mod_status` endpoint, when left accessible, exposes active connections, server load, worker states, and the last 512 requests (including URLs). In production environments behind a load balancer, this is often the most detailed picture of internal traffic patterns an attacker can get without intercepting anything. Restrict to `127.0.0.1` or remove entirely.

**readme.txt** — This one's embarrassing when it bites. A `readme.txt` or `README.md` in the web root typically contains the application version, sometimes setup instructions, sometimes default credentials from the initial install. Nikto finds it instantly. Delete it or move it out of the web root before deploying.

---

## On the Two False Positives

Nikto generated two findings that didn't apply to this server:

1. **`/%2e/` — Weblogic directory traversal check.** This fires for all servers, but the vulnerability only affects Weblogic. Python SimpleHTTP returns 404.
2. **PHP info disclosure probe.** PHP is not running on this server. The probe fires anyway because Nikto doesn't know the tech stack before it starts scanning.

These are expected. Nikto is a *breadth scanner* — it fires probes across many technology categories and lets the analyst filter results by relevance. The alternative (only firing probes that definitely apply) would require fingerprinting the target first, which adds time and reduces coverage.

SecurityClaw's AI layer handles this by cross-referencing Nikto findings with the target's known technology stack. PHP-specific findings against a known non-PHP server are flagged as noise before they reach the report. The analyst sees clean, stack-relevant results — not a list of every probe Nikto fired.

---

## What SecurityClaw Does With This

The raw Nikto output is noisy. Seventeen findings across severity levels, two false positives, a mix of planted and real issues — an analyst reviewing this manually has to understand the server stack, cross-reference severities, and figure out which findings to prioritise.

SecurityClaw's analysis layer:

1. **Stack-aware FP filtering** — removes Weblogic and PHP probes when the target isn't running those technologies
2. **Cross-tool correlation** — if `.git/HEAD` is exposed here, does TruffleHog also find secrets in the reconstructed repo? (See our [TruffleHog v3 demo](/articles/securityclaw-trufflehog-v3-live-secret-verification-demo-2026/))
3. **Business impact categorisation** — `.git/HEAD` exposure scores HIGH because of what it enables downstream, regardless of the raw finding severity

The correlation point matters. A `.git/HEAD` exposure finding and a TruffleHog `STRIPE_KEY` finding aren't two separate issues — they're the same attack path at two stages. SecurityClaw surfaces them together.

---

## Pairing Nikto With Other Scans

Nikto is a web misconfiguration scanner. It's not trying to be Burp Suite. It finds the obvious errors that shouldn't survive a deployment review — the `.git` exposure, the backup archive, the debug file, the missing headers.

For the broader picture:

- **Directory enumeration**: Gobuster found 10/10 hidden paths (including backup files and the admin panel) in [4.79 seconds in our demo](/articles/securityclaw-gobuster-directory-enumeration-demo-2026/) — it goes deeper than Nikto on path discovery
- **Secret detection in source**: If Nikto finds `.git/HEAD`, TruffleHog should immediately follow to enumerate what's in the repository
- **Dependency scanning**: The `.git/HEAD` exposure on the demo server also gave us access to `package.json` — triggering a follow-on npm audit run

These tools work in sequence. Nikto finds the doors; the other tools check what's behind them.

---

## Run It

Nikto is pre-installed on SecurityClaw's Kali environment. Against your own server or a staging instance you control:

```bash
nikto -h https://your-staging-server.example.com -nointeractive -maxtime 120s
```

Run it before your next deployment. Nikto finds the issues that deploy checklists miss — the backup archive someone created while debugging, the test file from last sprint, the `.git` directory that appeared when someone redeployed with the wrong method.

Four seconds. Against a controlled server, it found everything.

Run it against yours.

---

*SecurityClaw is the automated recon and vulnerability assessment platform built by the ClawWorks security team. This demo ran on a controlled environment — all findings are from intentionally misconfigured infrastructure. Tools used: Nikto v2.5.0. Part of the SecurityClaw demo series: [Gobuster](/articles/securityclaw-gobuster-directory-enumeration-demo-2026/) · [Gitleaks](/articles/securityclaw-gitleaks-git-history-secret-detection-demo-2026/) · [TruffleHog](/articles/securityclaw-trufflehog-v3-live-secret-verification-demo-2026/) · [Nuclei](/articles/securityclaw-nuclei-misconfiguration-scanner-demo-2026/)*
