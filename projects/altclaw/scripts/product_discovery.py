#!/usr/bin/env python3
"""
AltClaw Product Discovery Automation

Scans recent research files for product mentions and generates discovery reports
for manual validation. Does NOT automatically add products - generates candidates
for human review.

Usage:
    python3 product_discovery.py [--days N] [--dry-run]

"""

import argparse
import re
import os
from datetime import datetime, timedelta
from pathlib import Path

# Project paths
WORKSPACE = Path("/home/delmar/.openclaw/workspace")
RESEARCH_DIR = WORKSPACE / "projects/security/research"
VALIDATED_PRODUCTS = WORKSPACE / "projects/altclaw/bughuntertools.com/VALIDATED_PRODUCTS.md"
DISCOVERY_LOG = WORKSPACE / "projects/altclaw/product-discovery-log.json"

# Product patterns to extract from research
PRODUCT_PATTERNS = [
    # Tools
    r"(?i)(burp suite|burp\s+professional|burp\s+pro)",
    r"(?i)(metasploit|msf)",
    r"(?i)(nmap|zenmap)",
    r"(?i)(wireshark)",
    # Hardware
    r"(?i)(wifi\s+adapter|wireless\s+adapter|alfa\s+[A-Z0-9]+)",
    r"(?i)(yubikey|hardware\s+key|security\s+key)",
    r"(?i)(raspberry\s+pi|arduino)",
    r"(?i)(flipper\s+zero)",
    r"(?i)(usb\s+rubber\s+ducky)",
    # Laptops
    r"(?i)(thinkpad|dell\s+xps|asus\s+rog|macbook)",
    # Books
    r"(?i)(hacker\'s?\s+handbook|penetration\s+test\w*\s+guide)",
    r"(?i)(black\s+hat\s+python|gray\s+hat)",
]


def load_discovery_log():
    """Load previous discoveries to avoid duplicates"""
    if DISCOVERY_LOG.exists():
        import json
        with open(DISCOVERY_LOG) as f:
            return json.load(f)
    return {"discovered": [], "rejected": []}


def save_discovery_log(log):
    """Save discovery log"""
    import json
    with open(DISCOVERY_LOG, 'w') as f:
        json.dump(log, f, indent=2)


def get_validated_products():
    """Extract already validated ASINs to avoid duplicates"""
    if not VALIDATED_PRODUCTS.exists():
        return set()
    
    content = VALIDATED_PRODUCTS.read_text()
    asins = re.findall(r'\*\*ASIN:\*\*\s+([A-Z0-9]{10})', content)
    return set(asins)


def scan_research_files(days=7):
    """Scan recent research files for product mentions"""
    findings = []
    start_date = datetime.now() - timedelta(days=days)
    
    if not RESEARCH_DIR.exists():
        print(f"⚠️  Research directory not found: {RESEARCH_DIR}")
        return findings
    
    for research_file in RESEARCH_DIR.glob("*.md"):
        # Check if file is recent enough
        mtime = datetime.fromtimestamp(research_file.stat().st_mtime)
        if mtime < start_date:
            continue
        
        content = research_file.read_text()
        
        # Search for product patterns
        for pattern in PRODUCT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "product": match,
                    "source_file": research_file.name,
                    "date": mtime.strftime("%Y-%m-%d")
                })
    
    return findings


def generate_discovery_report(findings, validated_asins):
    """Generate markdown report of discoveries"""
    report = f"""# Product Discovery Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M GMT")}
**Scan Period:** Last 7 days
**Findings:** {len(findings)} products mentioned
**Already Validated:** {len(validated_asins)} ASINs

---

## New Product Candidates

"""
    
    # Deduplicate findings
    unique_products = {}
    for finding in findings:
        product = finding["product"].lower()
        if product not in unique_products:
            unique_products[product] = finding
    
    if not unique_products:
        report += "No new product candidates found in recent research.\n"
    else:
        for product, info in unique_products.items():
            report += f"### {info['product']}\n"
            report += f"- **Mentioned in:** {info['source_file']}\n"
            report += f"- **Date:** {info['date']}\n"
            report += f"- **Status:** Manual validation required\n"
            report += f"- **Action:** Search Amazon, find ASIN, verify credibility\n\n"
    
    report += """
---

## Next Steps

For each candidate:
1. Search Amazon for product
2. Find ASIN (10-character code)
3. Verify product has credible reviews/sources
4. Add to VALIDATED_PRODUCTS.md with format:

```markdown
### Product Name
- **ASIN:** ASIN_HERE
- **Price:** ~$XX
- **Commission:** X% (~$XX)
- **URL:** https://www.amazon.com/dp/ASIN_HERE?tag=altclaw-20
- **Why Recommended:** [Explain with source citation]
- **Status:** ✅ Validated YYYY-MM-DD
```

5. Run extract-asins.sh to verify it's picked up
6. Commit changes
"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="AltClaw Product Discovery")
    parser.add_argument("--days", type=int, default=7, help="Days of research to scan")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()
    
    print("=== AltClaw Product Discovery ===\n")
    
    # Load state
    log = load_discovery_log()
    validated_asins = get_validated_products()
    print(f"✓ Loaded {len(validated_asins)} validated products")
    
    # Scan research files
    print(f"📖 Scanning research files (last {args.days} days)...")
    findings = scan_research_files(args.days)
    print(f"✓ Found {len(findings)} product mentions")
    
    if not findings:
        print("\n✅ No new products to validate")
        return
    
    # Generate report
    report = generate_discovery_report(findings, validated_asins)
    
    # Save report
    report_path = WORKSPACE / "projects/altclaw/product-discovery-report.md"
    if not args.dry_run:
        report_path.write_text(report)
        print(f"\n✓ Report saved: {report_path}")
        print(f"\n📋 Review report and manually validate products")
    else:
        print("\n=== DRY RUN - Report Preview ===")
        print(report[:500] + "...")
    
    # Update log
    for finding in findings:
        if finding not in log["discovered"]:
            log["discovered"].append(finding)
    
    if not args.dry_run:
        save_discovery_log(log)


if __name__ == "__main__":
    main()
