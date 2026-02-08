#!/bin/bash

# Validated ASINs from VALIDATED_PRODUCTS.md
VALID_ASINS=(
    "1118026470"  # Web App Hacker's Handbook (Paperback)
    "B005LVQA9S"  # Web App Hacker's Handbook (Kindle)
    "1718501129"  # Black Hat Python
    "159327288X"  # Metasploit Guide
    "B00X4WHP5K"  # Practical Cloud Security
    "1394180071"  # Security+ Study Guide
    "B07HBD71HL"  # YubiKey 5 NFC
    "B00VEEBOPG"  # Alfa WiFi Adapter
    "B089ZZ8DTV"  # Raspberry Pi 4 Kit
)

echo "=== Quality Check Report ==="
echo ""

# Check for placeholder links
echo "1. Checking for placeholder links..."
if grep -r 'href="#"' *.html articles/*.html 2>/dev/null; then
    echo "❌ Found placeholder links"
    exit 1
else
    echo "✓ No placeholder links found"
fi

echo ""
echo "2. CRITICAL: Validating Amazon affiliate links..."
amazon_links=$(grep -roh 'amazon.com/dp/[^"?]*' *.html articles/*.html 2>/dev/null | cut -d'/' -f3 | sort -u)
invalid_found=0

if [ -n "$amazon_links" ]; then
    for asin in $amazon_links; do
        valid=0
        for valid_asin in "${VALID_ASINS[@]}"; do
            valid_asin_clean=$(echo "$valid_asin" | awk '{print $1}')
            if [ "$asin" == "$valid_asin_clean" ]; then
                valid=1
                echo "✓ ASIN $asin validated"
                break
            fi
        done
        
        if [ $valid -eq 0 ]; then
            echo "❌ INVALID ASIN: $asin (not in VALIDATED_PRODUCTS.md)"
            invalid_found=1
        fi
    done
    
    if [ $invalid_found -eq 1 ]; then
        echo ""
        echo "❌ COMMIT BLOCKED: Invalid Amazon ASINs found"
        echo "Fix: Use only ASINs from VALIDATED_PRODUCTS.md"
        exit 1
    fi
else
    echo "No Amazon links found"
fi

echo ""
echo "3. Checking for required meta tags..."
if grep -q '<meta name="description"' *.html articles/*.html 2>/dev/null; then
    echo "✓ Description meta found"
else
    echo "❌ Missing meta description"
fi

if grep -q 'application/ld+json' *.html articles/*.html 2>/dev/null; then
    echo "✓ Schema markup found"
else
    echo "❌ Missing Schema.org markup"
fi

echo ""
echo "✅ All critical quality checks passed - safe to commit"
