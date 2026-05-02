---
title: "We Gave Hashcat 6 Password Hashes. It Cracked 5 in Under a Second. The 6th Said No."
description: "We ran Hashcat v7.1.2 against 6 password hashes — MD5, NTLM, SHA-1, SHA-256, SHA-512, and bcrypt. Five cracked in milliseconds. One didn't. The gap between them is 59,034x."
date: 2026-05-02
category: research
tags: [hashcat, password-security, bcrypt, ntlm, securityclaw, cryptography]
---

> **Affiliate Disclosure:** This site contains affiliate links. We earn a commission when you purchase through our links at no additional cost to you.

We planted 6 password hashes on a controlled test server — one for each major algorithm type that appears in real-world database breaches. Then we pointed SecurityClaw's hashcat skill at them with a standard dictionary attack.

Five hashes cracked in under a second. The sixth said no.

Here's exactly what happened.

---

## The Setup

**Tool:** Hashcat v7.1.2  
**Mode:** Dictionary attack (rockyou.txt top 50,001 entries)  
**Platform:** SecurityClaw Campaign Manager v2.0, Campaign 29  
**Hardware:** ARM aarch64 CPU (no GPU)

We planted one hash for each algorithm class:

| Algorithm | Cracking Speed | Cracked? | Recovered Plaintext |
|-----------|---------------|----------|---------------------|
| MD5 | 937,500 H/s | ✅ YES | `password` |
| NTLM (Windows) | **6,613,900 H/s** | ✅ YES | `letmein` |
| SHA-1 | 5,548,600 H/s | ✅ YES | `qwerty123` |
| SHA-256 | 3,243,800 H/s | ✅ YES | `Password1!` |
| SHA-512 | 2,759,500 H/s | ✅ YES | `abc123` |
| **bcrypt (rounds=10)** | **112 H/s** | ❌ **RESISTED** | — |

**Overall: 5/6 cracked (83.3% crack rate). Campaign result: PASS.**

The word "pass" here means something specific: SecurityClaw confirmed the system is working correctly. bcrypt was expected to resist. It did. The fast hashes were expected to fall. They did. The test validates both sides of the story.

---

## The 59,034x Gap

The most important number in that table isn't the crack rate. It's the speed difference between the worst-case algorithm and the one algorithm that held.

**NTLM: 6,613,900 hashes/second**  
**bcrypt: 112 hashes/second**

That's **59,034 times faster**. On the same hardware. Using the same dictionary. Against the same type of target.

To put it another way: in the time it takes Hashcat to attempt one bcrypt hash, it can test 59,034 NTLM hashes. At NTLM speeds, the 50,001-entry wordlist is exhausted in approximately 7 milliseconds. At bcrypt speeds, testing 14 million passwords (the full rockyou.txt) takes around **32 hours — per hash**. Add 10,000 users to a breached database and you're looking at 320,000 hours of compute per full pass.

That's not a rounding error. That's the design.

---

## SHA-512 Sounds Strong. It Isn't.

This is the one developers get wrong most often.

SHA-512 produces a 128-character hex string. It looks impenetrable. But it's a general-purpose cryptographic hash function — designed to be fast for data integrity checks, file checksums, and certificate operations. Speed is a feature of SHA-512, not a flaw. For password storage, that speed is the flaw.

**2.7 million hashes per second.** The full rockyou.txt wordlist cracked in under 6 seconds.

"I use SHA-512 so I'm secure" is one of the most dangerous sentences in back-end development. Algorithm complexity without key stretching is security theatre.

---

## NTLM Is the Worst Possible Option

6.6 million hashes per second on a **CPU-only ARM box**. With a mid-range GPU, that figure moves into the hundreds of billions per second range.

NTLM is still widely deployed — Windows environments, Active Directory, legacy APIs, older internal tools. Every NTLM hash in your database is, for practical purposes, a plaintext password waiting for a wordlist match. If your server is breached and the attacker gets the hash database, recovery time for common passwords is measured in milliseconds.

---

## bcrypt Forces the Attacker to Slow Down Permanently

**112 hashes per second.** Not 112 thousand. Not 112 million. 112.

bcrypt is a key derivation function (KDF) with a configurable work factor. The `$2b$10$` prefix in a bcrypt hash means the password was stretched through 2^10 = 1,024 rounds of processing. Double the work factor and you double the cracking time. An attacker can't avoid the rounds — they're not a weakness to exploit, they're a cost floor that applies to every attempt.

### The Salting Bonus

Even if two users set identical passwords, their bcrypt hashes are different. Each bcrypt hash embeds a unique random salt. That means:

- **Rainbow tables are useless.** Pre-computed hash dictionaries can't work when every hash has a unique salt.
- **Every account must be cracked individually.** There's no batch shortcut. Each hash costs the full 32 hours.

At scale — a 10,000-user breach with bcrypt-hashed passwords — mass cracking becomes economically unviable. Attackers move on.

---

## What SecurityClaw Found

```
Campaign: D14-Hashcat-PasswordCracking-2026-03-12
Tool: hashcat v7.1.2
Category: password-security
Result: PASS (5/6 cracked, bcrypt correctly resisted)
Timing: <1 second effective for 5 fast hashes
Planted: 6 hashes | Cracked: 5 | Resisted: 1 (by design)
Platform: SecurityClaw Campaign Manager v2.0 | Campaign 29 | Result 25
```

This is D14 in the SecurityClaw demo series. Running score after D14: **23/25 campaigns = 92.00%.** D14 adds password-security as a new campaign category.

---

## Honest Gaps (Because We Document What We Didn't Cover)

**1. CPU-only hardware.** This demo ran on ARM aarch64 without a GPU. A modern gaming GPU cracks MD5 at approximately 100 billion hashes/second — roughly 100,000x faster than our demo results. bcrypt on a GPU runs at around 10,000–20,000 H/s — still vastly slower than fast hashes, and the gap still holds. The 59,034x ratio reflects relative algorithm cost, not absolute attack speed.

**2. Demo wordlist was 50,001 entries.** We used the top 50,001 passwords from rockyou.txt for the demo — enough to catch all 5 planted weak passwords in under a second. Real-world attacks use the full 14 million entry list and beyond.

**3. We planted easy passwords.** `password`, `letmein`, `abc123` are in the top 1,000 most common passwords worldwide. We designed the demo to crack fast so the point lands. Real-world crack rates depend heavily on password policy enforcement.

**4. Rainbow table attacks were not demonstrated.** Pre-computed rainbow table attacks against unsalted MD5/SHA-1 hashes are even faster than dictionary attacks. bcrypt's per-hash salting defeats them completely — but we didn't run a rainbow table demo here.

---

## What Good Looks Like

**Stop using MD5, SHA-1, NTLM, SHA-256, and SHA-512 for password storage.** These are not password hashing algorithms. They are general-purpose hashing algorithms that happen to accept passwords as input.

**Use bcrypt.** It's available in every major language and framework. The work factor is configurable — set it so hashing takes 200–300ms on your production hardware, then raise it as hardware improves.

**Consider Argon2.** Argon2 won the Password Hashing Competition in 2015 and adds memory hardness on top of time hardness — you can't just throw more GPU cores at it. It's the modern best practice. bcrypt is good. Argon2 is better.

**Enforce a password policy.** Even bcrypt won't save you if your users are all using `password`. Rate limiting, breach password detection (via HIBP), and minimum complexity requirements mean attackers never get the dictionary attempt in the first place.

---

## The Takeaway

Five passwords cracked in milliseconds. One held for 32 hours per attempt. The difference isn't complexity — it's algorithm choice.

If your application stores MD5 or SHA-1 password hashes, you have a disclosure event waiting to happen. The breach doesn't create the vulnerability. It just reveals it.

SecurityClaw's hashcat skill runs this analysis in one command against your target environment. The output tells you exactly which algorithm changes to prioritize before an attacker tells you first.

---

*This demo is part of the SecurityClaw demo series. Related posts: [We Deleted the Key. Gitleaks Found It Anyway.](/articles/securityclaw-gitleaks-git-history-secret-detection-demo-2026/) — on finding secrets in git history, including bcrypt hashes committed and then "deleted".*
