#!/usr/bin/env python3
"""
Fix meta descriptions for bughuntertools.com
Target: 140-160 chars, unique, keyword-rich, search-engine friendly
"""
import re
import os

ARTICLES_DIR = "/home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com/src/articles"

# Maps: filename -> new description (only files needing changes)
FIXES = {
    "adobe-after-effects-cve-2026-21329.njk": "Critical CVE-2026-21329: Adobe After Effects use-after-free enables RCE in version 25.6 and earlier. Technical breakdown and bug bounty testing guide.",
    "aeternum-botnet-blockchain-c2-polygon-ethereum.njk": "Aeternum botnet stores C2 instructions in Ethereum smart contracts on Polygon — no servers, no domains, no takedown. How blockchain-based C2 works and how to detect it.",
    "automated-penetration-testing-guide-2026.njk": "AI-powered and automated pentesting in 2026: how it works, what it covers, what to look for in a platform, and how to get started.",
    "azure-sdk-rce-cve-2026-21531.njk": "CVSS 9.8 deserialization bug in Azure AI Language Python SDK enables unauthenticated RCE. Any app using azure-ai-language-conversations 1.0.0-beta is exposed.",
    "beyondtrust-rce-cve-2026-1731.njk": "CVSS 9.9 pre-auth RCE in BeyondTrust Remote Support via unauthenticated WebSocket command injection. 8,500+ exposed instances globally. Patch immediately.",
    "chainlit-ai-vulnerabilities-cve-2026-22218.njk": "CVE-2026-22218 and CVE-2026-22219 in Chainlit AI framework enable cloud takeovers via file read and SSRF attacks. Testing AI applications for security flaws.",
    "cisco-sdwan-cve-2026-20127-auth-bypass.njk": "Cisco Catalyst SD-WAN CVSS 10.0 auth bypass actively exploited by nation-state UAT-8616. CISA Emergency Directive 26-03 mandates federal patching by Feb 27, 2026.",
    "claude-code-security-vs-penetration-testing.njk": "Anthropic's Claude Code Security launched February 21, 2026. What it catches, where it stops, and why active penetration testing still matters for your security team.",
    "dell-recoverpoint-cve-2026-22769.njk": "Dell RecoverPoint CVE-2026-22769: hardcoded credentials exploited by Silk Typhoon (UNC6201) since mid-2024. CISA KEV listing with 3-day patch mandate. Act now.",
    "firefox-spidermonkey-wasm-gc-rce.njk": "A & vs | typo in Firefox SpiderMonkey's Wasm GC engine causes type confusion leading to renderer RCE — affecting 200M+ users via any malicious webpage.",
    "gcp-vertex-ai-bucket-squatting-cve-2026-2473.njk": "Google patches Vertex AI CVE-2026-2473: predictable bucket names exposed AI models to theft and cross-tenant code execution. Bug bounty writeup and detection guidance.",
    "malicious-go-module-xinfeisoft-crypto-apt31-rekoobe.njk": "Typosquatted Go module posed as golang.org/x/crypto to steal SSH credentials and install APT31's Rekoobe backdoor. Attack mechanics and detection walkthrough.",
    "microsoft-patch-tuesday-february-2026-zero-days.njk": "Microsoft February 2026 Patch Tuesday: 59 CVEs including 6 actively exploited zero-days in Windows Shell, MSHTML, and RDP. Priority patches for security teams.",
    "model-distillation-attacks-deepseek-claude-anthropic-2026.njk": "DeepSeek, Moonshot AI, and MiniMax extracted Claude via 16M fraudulent API calls — caught by Anthropic. How model distillation attacks work and how to defend AI APIs.",
    "mshtml-cve-2026-21513.njk": "CVE-2026-21513 MSHTML zero-day exploited in the wild: CVSS 8.8 security feature bypass lets attackers evade Mark-of-the-Web protections. Patch Tuesday priority.",
    "n8n-rce-cve-2026-21858-critical-workflow-vulnerability.njk": "CVSS 10.0 n8n CVE-2026-21858 enables unauthenticated RCE in workflow automation. Affected versions, exploitation methods, and remediation steps explained.",
    "n8n-rce-cve-2026-21858.njk": "CVSS 10.0 critical vulnerability in n8n enables unauthenticated RCE. Technical breakdown of CVE-2026-21858 and a complete mitigation guide for bug hunters.",
    "roguepilot-github-copilot-prompt-injection.njk": "Passive prompt injection in GitHub Copilot leaks GITHUB_TOKEN from Codespaces with zero user interaction. Orca Security's RoguePilot disclosure and detection guidance.",
    "scarcruft-ruby-jumper-north-korea-zoho-workdrive-c2.njk": "ScarCruft (APT37) used Zoho WorkDrive as C2 in the 'Ruby Jumper' campaign, combined with USB malware to reach air-gapped targets. Living-off-trusted-sites meets physical relay.",
    "security-lab-setup-guide-2026.njk": "Build a professional security testing lab in 2026: researched recommendations for pentesting laptops, Kali-compatible WiFi adapters, and hardware security tools.",
    "security-roundup-2026-02-17.njk": "Weekly roundup: vLLM RCE, six n8n CVEs, Azure Functions info disclosure, AI-assisted AWS breach, HackerOne's $4.3M payout week, and top tools for bug hunters.",
    "unc2814-gridtide-google-sheets-c2-apt.njk": "Chinese APT UNC2814 used Google Sheets cells as C2 in the GRIDTIDE campaign, hitting 53 organisations in 42 countries before Google's disruption on Feb 25, 2026.",
    "vllm-rce-cve-2026-22778.njk": "CVE-2026-22778: CVSS 9.8 unauthenticated RCE in vLLM GPU clusters discovered by Orca Security. Technical breakdown and mitigation for LLM inference infrastructure.",
    "vscode-extensions-cve-2025-65717.njk": "CVE-2025-65717: four popular VS Code extensions expose 125M developers to RCE and file exfiltration. Three of four vulnerabilities remain unpatched — details inside.",
    "why-your-security-scanner-isnt-a-penetration-test.njk": "Vulnerability scanners find known CVEs. Penetration tests find what attackers exploit. The critical difference — and what you risk by relying on scans alone.",
    "zyxel-cve-2025-13942-unauthenticated-rce-routers.njk": "CVE-2025-13942: command injection in 12+ Zyxel models exposes 120,000 devices to unauthenticated RCE via UPnP SOAP. Security updates released February 25, 2026.",
    # Index page — slightly short, give it more context
    "index.njk": "CVE analysis, security tool reviews, and practical pentesting guides for bug bounty hunters and penetration testers. New articles published weekly.",
}

def fix_description(filepath, new_desc):
    with open(filepath, 'r') as f:
        content = f.read()
    # Match the description field in YAML front matter
    # Handles both quoted and unquoted descriptions
    new_content = re.sub(
        r'^(description:\s*)(.+)$',
        lambda m: m.group(1) + new_desc,
        content,
        count=1,
        flags=re.MULTILINE
    )
    if new_content == content:
        print(f"  ⚠️  No change made to {os.path.basename(filepath)}")
        return False
    with open(filepath, 'w') as f:
        f.write(new_content)
    return True

updated = 0
skipped = 0
for filename, new_desc in FIXES.items():
    filepath = os.path.join(ARTICLES_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  ❌ Not found: {filename}")
        skipped += 1
        continue
    char_count = len(new_desc)
    if fix_description(filepath, new_desc):
        print(f"  ✅ {filename} ({char_count} chars)")
        updated += 1
    else:
        skipped += 1

print(f"\nDone: {updated} updated, {skipped} skipped")
