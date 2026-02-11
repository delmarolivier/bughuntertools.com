#!/bin/bash
# Extract all ASINs from VALIDATED_PRODUCTS.md
# This is the single source of truth for valid ASINs

cd /home/delmar/.openclaw/workspace/projects/altclaw/bughuntertools.com

if [ ! -f "VALIDATED_PRODUCTS.md" ]; then
    echo "❌ ERROR: VALIDATED_PRODUCTS.md not found"
    exit 1
fi

echo "=== Valid ASINs from VALIDATED_PRODUCTS.md ==="
echo ""

asins=$(grep -oP '(?<=\*\*ASIN:\*\* )[A-Z0-9]{10}' VALIDATED_PRODUCTS.md | sort -u)
count=$(echo "$asins" | wc -l)

echo "$asins"
echo ""
echo "Total: $count ASINs"
