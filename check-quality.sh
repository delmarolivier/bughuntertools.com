#!/bin/bash

echo "=== Comprehensive Site Testing ==="
echo ""

cd /home/delmar/.openclaw/workspace/projects/altclaw/bughuntertools.com

# 1. Check all HTML files for broken internal links
echo "1. Testing all internal links..."
broken_links=0

for file in index.html privacy.html articles/*.html; do
    if [ -f "$file" ]; then
        echo "Checking $file..."
        
        # Extract all href links
        links=$(grep -oP 'href="[^"]*"' "$file" | sed 's/href="//g' | sed 's/"//g')
        
        for link in $links; do
            # Skip external links and anchors
            if [[ $link == http* ]] || [[ $link == \#* ]]; then
                continue
            fi
            
            # Convert relative links to file paths
            if [[ $file == articles/* ]]; then
                base_dir="articles"
            else
                base_dir="."
            fi
            
            # Resolve the link
            if [[ $link == /* ]]; then
                # Absolute path from root
                target_file="index.html"
                if [[ $target_file == */ ]]; then
                    target_file="${target_file}index.html"
                fi
            elif [[ $link == ../* ]]; then
                # Parent directory
                target_file="${link#../}"
            else
                # Relative to current directory
                if [[ $base_dir == "articles" ]]; then
                    target_file="articles/$link"
                else
                    target_file="$link"
                fi
            fi
            
            # Check if target exists
            if [ ! -f "$target_file" ] && [ ! -d "$target_file" ]; then
                echo "  ❌ BROKEN: $link (in $file) → $target_file not found"
                broken_links=$((broken_links + 1))
            fi
        done
    fi
done

if [ $broken_links -gt 0 ]; then
    echo "❌ Found $broken_links broken internal links"
    exit 1
else
    echo "✓ All internal links valid"
fi

echo ""
echo "2. Checking CSS paths..."
css_errors=0

for file in articles/*.html; do
    if grep -q 'href="css/style.css"' "$file"; then
        echo "❌ $file: Wrong CSS path (should be ../css/style.css)"
        css_errors=$((css_errors + 1))
    fi
done

if [ $css_errors -gt 0 ]; then
    echo "❌ Found $css_errors CSS path errors"
    exit 1
else
    echo "✓ All CSS paths correct"
fi

echo ""
echo "3. Checking for duplicate content in navigation..."

# Check that all nav menus are consistent
nav_pattern='<a href="/">Home</a>.*<a href="/articles/">Articles</a>.*<a href="/articles/security-testing-tools-2026.html">Tools</a>.*<a href="/privacy.html">Privacy</a>'

inconsistent=0
for file in index.html articles/*.html; do
    if [ -f "$file" ]; then
        if ! grep -Pzo "$nav_pattern" "$file" >/dev/null 2>&1; then
            # Try simpler check
            if ! grep -q '<a href="/articles/security-testing-tools-2026.html">Tools</a>' "$file"; then
                echo "⚠️  $file: Navigation might be inconsistent"
                inconsistent=$((inconsistent + 1))
            fi
        fi
    fi
done

if [ $inconsistent -gt 0 ]; then
    echo "⚠️  Some navigation menus might be inconsistent (check manually)"
else
    echo "✓ Navigation consistent"
fi

echo ""
echo "4. Running HTMLHint validation..."
htmlhint index.html articles/*.html 2>&1 | grep -E "error|warning|✓" | head -20

echo ""
echo "5. Checking Amazon affiliate links..."
amazon_links=$(grep -roh 'amazon.com/dp/[^"?]*' *.html articles/*.html 2>/dev/null | cut -d'/' -f3 | sort -u)

# Extract ASINs dynamically from VALIDATED_PRODUCTS.md (single source of truth)
if [ -f "VALIDATED_PRODUCTS.md" ]; then
    VALID_ASINS=($(grep -oP '(?<=\*\*ASIN:\*\* )[A-Z0-9]{10}' VALIDATED_PRODUCTS.md | sort -u))
    echo "Loaded ${#VALID_ASINS[@]} ASINs from VALIDATED_PRODUCTS.md"
else
    echo "❌ ERROR: VALIDATED_PRODUCTS.md not found"
    exit 1
fi

invalid_found=0
if [ -n "$amazon_links" ]; then
    for asin in $amazon_links; do
        valid=0
        for valid_asin in "${VALID_ASINS[@]}"; do
            if [ "$asin" == "$valid_asin" ]; then
                valid=1
                break
            fi
        done
        
        if [ $valid -eq 0 ]; then
            echo "❌ INVALID ASIN: $asin"
            invalid_found=1
        fi
    done
    
    if [ $invalid_found -eq 0 ]; then
        echo "✓ All Amazon ASINs valid"
    fi
else
    echo "No Amazon links found"
fi

echo ""
echo "=== Site Testing Complete ==="

if [ $broken_links -gt 0 ] || [ $css_errors -gt 0 ] || [ $invalid_found -gt 0 ]; then
    echo "❌ BLOCKING COMMIT: Critical errors found"
    exit 1
else
    echo "✅ All critical tests passed"
fi
