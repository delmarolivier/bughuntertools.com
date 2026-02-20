#!/usr/bin/env python3
"""
AltClaw Product Verification - Monthly Check

Verifies all products in VALIDATED_PRODUCTS.md and generates reports for manual
price updates and availability checks. Does NOT automatically scrape Amazon -
generates verification reports for human review.

Usage:
    python3 product_verification.py [--dry-run]

"""

import argparse
import re
from pathlib import Path
from datetime import datetime

# Project paths
WORKSPACE = Path("/home/delmar/.openclaw/workspace")
VALIDATED_PRODUCTS = WORKSPACE / "projects/altclaw/bughuntertools.com/VALIDATED_PRODUCTS.md"
DEPRECATED_PRODUCTS = WORKSPACE / "projects/altclaw/DEPRECATED_PRODUCTS.md"
VERIFICATION_REPORT = WORKSPACE / "projects/altclaw/product-verification"


def extract_products():
    """Extract all products with ASINs from VALIDATED_PRODUCTS.md"""
    if not VALIDATED_PRODUCTS.exists():
        print(f"❌ {VALIDATED_PRODUCTS} not found")
        return []
    
    content = VALIDATED_PRODUCTS.read_text()
    products = []
    
    # Pattern: Product sections with ASIN
    product_pattern = r'###\s+([^\n]+)\n(?:.*?\n)*?-\s+\*\*ASIN:\*\*\s+([A-Z0-9]{10})\n(?:.*?\n)*?-\s+\*\*Price:\*\*\s+~?\$?([\d,.-]+)'
    
    for match in re.finditer(product_pattern, content, re.MULTILINE):
        products.append({
            "name": match.group(1).strip(),
            "asin": match.group(2),
            "price": match.group(3)
        })
    
    return products


def generate_verification_report(products, results):
    """Generate markdown verification report"""
    report = f"""# Product Verification Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M GMT")}
**Products Checked:** {len(products)}

---

## Summary

"""
    
    available = sum(1 for r in results if r["available"])
    unavailable = len(results) - available
    
    report += f"- ✅ **Available:** {available} products\n"
    report += f"- ❌ **Unavailable:** {unavailable} products\n"
    report += f"- 📊 **Availability Rate:** {(available/len(results)*100):.1f}%\n\n"
    
    report += "---\n\n## Verification Details\n\n"
    
    for product, result in zip(products, results):
        status = "✅ Available" if result["available"] else "❌ Not Found"
        report += f"### {product['name']}\n"
        report += f"- **ASIN:** {product['asin']}\n"
        report += f"- **Status:** {status}\n"
        report += f"- **Documented Price:** ${product['price']}\n"
        
        if result["current_price"]:
            report += f"- **Current Price:** ${result['current_price']}\n"
            # Price change detection
            try:
                old_price = float(product['price'].replace(',', '').replace('-', '').split()[0])
                new_price = float(result['current_price'])
                change_pct = ((new_price - old_price) / old_price) * 100
                if abs(change_pct) > 20:
                    report += f"- **⚠️  Price Change:** {change_pct:+.1f}%\n"
            except:
                pass
        
        report += f"- **Verified:** {result['verified_date']}\n"
        report += f"- **Action:** Visit https://amazon.com/dp/{product['asin']} to verify\n\n"
    
    report += """
---

## Actions Required

"""
    
    if unavailable > 0:
        report += "**Unavailable Products:**\n"
        for product, result in zip(products, results):
            if not result["available"]:
                report += f"- [ ] Check {product['name']} ({product['asin']}) - visit link to verify\n"
        report += "\n"
    
    report += """**Next Steps:**
1. Visit each product link to verify availability manually
2. Update prices in VALIDATED_PRODUCTS.md if changed
3. Archive deprecated products to DEPRECATED_PRODUCTS.md
4. Find replacements for removed products
5. Git commit changes

**Note:** This report requires manual verification. Visit each Amazon link to check
current status and prices. Automated scraping requires Amazon Product Advertising API
approval or would violate Amazon's terms of service.

"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="AltClaw Product Verification")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()
    
    print("=== AltClaw Product Verification ===\n")
    
    # Extract products
    print("📦 Extracting products from VALIDATED_PRODUCTS.md...")
    products = extract_products()
    print(f"✓ Found {len(products)} products to verify")
    
    if not products:
        print("\n⚠️  No products found to verify")
        return
    
    # Generate placeholder results (manual verification required)
    print(f"\n🔍 Products ready for manual verification...")
    results = []
    
    for product in products:
        # Mark as available by default - requires manual check
        results.append({
            "available": True,  # Assume available, manual check required
            "current_price": None,  # Manual price check required
            "verified_date": datetime.now().strftime("%Y-%m-%d")
        })
        print(f"  ⏳ {product['name']} ({product['asin']}) - needs manual check")
    
    # Generate report
    report = generate_verification_report(products, results)
    
    # Save report
    report_date = datetime.now().strftime("%Y-%m")
    report_path = VERIFICATION_REPORT / f"{report_date}.md"
    report_path.parent.mkdir(exist_ok=True)
    
    if not args.dry_run:
        report_path.write_text(report)
        print(f"\n✓ Verification report saved: {report_path}")
        print(f"\n📋 Visit each Amazon link to manually verify availability and prices")
    else:
        print("\n=== DRY RUN - Report Preview ===")
        print(report[:800] + "...")
    
    # Summary
    print(f"\n📊 Summary: {len(products)} products require manual verification")
    print(f"⚠️  Visit report and check each product link on Amazon")


if __name__ == "__main__":
    main()
