---
title: "15 Vulnerabilities in Your package.json. 2 Seconds to Find Them."
description: "We loaded a Node.js project with 8 deliberately outdated packages and ran SecurityClaw's npm audit skill against it. 15 vulnerabilities. 2 critical. Zero false positives. One package with no patch — not now, not ever. Here's what that means."
date: 2026-05-03
category: research
tags: [npm-audit, supply-chain-security, nodejs, dependency-scanning, cve]
---

You almost certainly have it installed. `npm audit` ships with every version of npm since npm 6 — which means it's on every Node.js developer's machine right now. It queries the GitHub Advisory Database, it runs in seconds, and it costs nothing.

Most developers only see it when it appears in CI logs — and even then, the `npm audit fix` reflex kicks in before anyone reads the output. That's how a Remote Code Execution vulnerability sits in `package.json` for three years without anyone noticing.

This is a live demo. We loaded a controlled Node.js project with 8 deliberately pinned-old packages and ran SecurityClaw's supply-chain scanner — powered by `npm audit` — against it. 15 vulnerabilities, 2 critical, zero false positives, all found in 2.1 seconds.

One of the findings has no fix. Not yet. Not ever.

---

## The Setup: 8 Packages, All Deliberately Broken

We built a controlled Node.js project and pinned 8 packages to vulnerable versions we knew were in the advisory database. Authorized environment, documented procedure. The goal was to confirm detection — not to find something new.

| Package | Version | Vulnerability | Severity | Fix |
|---|---|---|---|---|
| `node-serialize` | 0.0.4 | RCE via IIFE deserialization | 🔴 CRITICAL | **Abandoned — no fix. Replace entirely.** |
| `minimist` | 0.0.8 | Prototype Pollution | 🔴 CRITICAL | Update to ≥1.2.6 |
| `lodash` | 4.17.15 | Command Injection | 🟠 HIGH | Update to ≥4.17.21 |
| `axios` | 0.19.0 | Server-Side Request Forgery (SSRF) | 🟠 HIGH | Update to ≥1.6.0 |
| `express` | 4.16.0 | XSS via `response.redirect()` | 🟠 HIGH | Update to ≥4.19.2 |
| `marked` | 0.3.6 | XSS from data URIs | 🟠 HIGH | Update to ≥4.0.10 |
| `js-yaml` | 3.12.0 | Denial of Service | 🟠 HIGH | Update to ≥3.13.1 |
| `serialize-javascript` | 1.6.1 | Cross-Site Scripting | 🟠 HIGH | Update to ≥3.1.0 |

**Detection: 8/8 (100%). Total findings: 15 (2 critical, 10 high, 3 low). Scan time: 2.1 seconds. False positives: 0.**

---

## The Standout Finding: node-serialize RCE — No Fix Available

Every other finding in this list has a fix: bump a version number, run `npm update`, done. `node-serialize` is different.

`node-serialize` 0.0.4 contains a Remote Code Execution vulnerability via **Immediately Invoked Function Expression (IIFE) deserialization**. Here's the short version: if your application passes user-controlled data to `node-serialize.unserialize()`, an attacker can execute arbitrary code on the server. Not steal data. Not crash the process. Execute code.

The exploit class has been known since [2017](https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/). The package was last updated in 2015. The author is unreachable. **There is no patched version and there will never be one.**

npm audit surfaces this clearly:

```
node-serialize  <=0.0.4
Severity: critical
Remote Code Execution (RCE)
No fix available
Node path: ./node_modules/node-serialize
```

The phrase "No fix available" in a critical-severity npm advisory is genuinely unusual. The advisory exists. The CVE exists. The patch does not. The correct remediation is to remove the package entirely and replace its functionality with something maintained — `flatted`, `devalue`, or a purpose-built serialization solution that never executes what it deserializes.

The uncomfortable question: how many production `package.json` files still list `node-serialize` because it was added in 2016, `npm audit` was never run, and no one knew?

---

## Prototype Pollution: When One Bad Argument Contaminates Everything

`minimist` is the argument-parsing package behind half of Node.js CLI tooling. If you've used `webpack`, `mocha`, `browserify`, or hundreds of other tools, you've used minimist. Version 0.0.8 contains a prototype pollution vulnerability.

Prototype pollution in JavaScript means that an attacker can inject properties into `Object.prototype` — the base object that every JavaScript object inherits from. In practice: if you're running `minimist({__proto__: {admin: true}})`, suddenly `({}).admin === true` is `true` for every object in your process.

That's an authentication bypass. Not a theoretical one. An attacker who controls argument input can add `admin: true` to your base object and walk through every auth check that reads `if (user.admin)`.

The fix is a single version bump to `>=1.2.6`. The question is how many CLI-heavy Node.js projects are still running `0.0.x` because no one ran `npm audit` when minimist was a transitive dependency buried three levels deep in their `node_modules`.

---

## The Other Six: All Fixable, All Real

The remaining six findings are the more common pattern — packages that haven't been updated and have known vulnerabilities with available fixes:

**lodash 4.17.15** — Command Injection via `_.template()`. The lodash maintainers patched this in 4.17.21, a point release. Four minor patch numbers separate you from arbitrary command execution if you use lodash's template feature.

**axios 0.19.0** — Server-Side Request Forgery (SSRF). An application using this version of axios can be coerced into making requests to internal infrastructure — cloud metadata endpoints, internal services, anything on the network the server can reach. Patched in 1.6.0, which also included a major API cleanup.

**express 4.16.0** — XSS via `response.redirect()`. If your application calls `res.redirect()` with user-controlled data, this version reflects unsanitized values back to the browser. Patched in 4.19.2.

**marked 0.3.6** — XSS from data URIs. The markdown parser allows `data:` URIs in rendered output, which executes JavaScript in older browsers and some environments. Fixed in 4.0.10 with explicit data URI blocking.

**js-yaml 3.12.0** — Denial of Service via crafted YAML. Specially constructed input can cause the parser to consume unbounded memory and crash. Fixed in 3.13.1 with input bounds checking.

**serialize-javascript 1.6.1** — Cross-Site Scripting. The serializer fails to escape certain unicode characters, allowing script injection into server-side rendered output. Fixed in 3.1.0.

None of these are dramatic. All of them are real. All of them are fixable with version bumps that take five minutes.

---

## What npm audit Doesn't Catch

Part of the SecurityClaw brief on this demo requires being honest about scope.

**npm audit catches known vulnerable versions.** It does not catch:
- **Deliberately malicious packages** — a typosquatted `lodahs` that exfiltrates your environment on install won't show up in the advisory database. For that, you need a tool like Socket.dev or Snyk that analyses package behaviour.
- **Supply-chain injection** — a compromised maintainer publishing a malicious version of a legitimate package (like the `event-stream` compromise or the XZ Utils backdoor) may or may not have an advisory by the time you run `npm audit`.
- **Licence risk** — a GPL-licensed transitive dependency in a commercial project is a legal problem, not a CVE.
- **Abandonware without CVEs** — packages that are unmaintained but have no documented vulnerabilities don't appear. `node-serialize` showed up because there's an advisory. A dead package with undiscovered vulnerabilities doesn't.

The detection story here is 100% — 8/8 planted packages with published advisories, all found. That's the designed scope of `npm audit`, and SecurityClaw runs it correctly.

If you want to catch supply-chain injection at the registry level, pair `npm audit` with a dedicated registry-scanning tool. They do different jobs.

---

## The SecurityClaw Integration

SecurityClaw's supply-chain scanner runs `npm audit --json` as part of every project campaign, alongside network scanning, web vulnerability testing, and secrets detection. The output feeds into the same unified report — so a dependency risk in `package.json` appears alongside a misconfigured S3 bucket or an exposed `.env` file, with the same severity classification and the same remediation tracking.

Most developers who run `npm audit` manually do it once, see a wall of output, run `npm audit fix`, and close the terminal. SecurityClaw runs it automatically on every campaign and tracks changes over time — so if a new advisory drops for a package you updated last week, the next campaign flags it.

The `node-serialize` finding is a useful test case. `npm audit fix --force` won't help — there's no version to upgrade to. The fix is architectural: remove the package, replace the functionality, audit every code path that touched `unserialize()`. That's a decision that requires a human, not a script. What SecurityClaw does is make sure the decision gets surfaced — not buried in CI noise.

---

## Run It Now

`npm audit` is already installed. If you have Node.js, you have it.

```bash
cd your-project
npm audit
```

If you haven't run it recently on a project that's been running for a year or more, the output will surprise you. Some findings will be false urgency — minor vulnerabilities in dev-only packages. Some will be genuine risks that have been sitting in `node_modules` since someone added a convenience library in a pull request no one reviewed carefully.

One of them might say "No fix available."

Run SecurityClaw's supply-chain scanner for the full picture: dependency findings alongside network exposure, web vulnerabilities, and secret detection — in a single report, automated across every campaign.

---

*SecurityClaw demo series — D3. Supply chain scanner: npm audit skill. Authorized test environment, 2026-03-03. Full campaign data: campaign_id=3, result_id=3.*

*For the supply-chain scanner demo covering malicious packages and typosquatting detection, see the [SecurityClaw SANDWORM_MODE demo](/articles/securityclaw-supply-chain-scanner-sandworm-mode-demo-2026/).*
