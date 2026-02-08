#!/bin/bash
echo "=== Quality Check Report ==="
echo ""

echo "1. Checking for broken internal links..."
grep -o 'href="#[^"]*"' index.html | sort -u

echo ""
echo "2. Checking for placeholder links..."
grep -n 'href="#"' index.html || echo "✓ No placeholder links found"

echo ""
echo "3. Checking for missing alt tags on images..."
grep -c '<img' index.html && echo "Images found, checking alt..." && grep '<img' index.html | grep -v 'alt=' || echo "✓ No images or all have alt tags"

echo ""
echo "4. Checking external links..."
grep -o 'https://[^"]*' index.html | sort -u

echo ""
echo "5. Checking meta tags..."
grep -i '<meta name="description"' index.html && echo "✓ Description meta found" || echo "✗ Missing description"

echo ""
echo "6. Checking schema markup..."
grep -i 'schema.org' index.html && echo "✓ Schema markup found" || echo "✗ Missing schema"

echo ""
echo "7. File sizes..."
ls -lh *.html css/*.css

echo ""
echo "8. HTML validation (basic)..."
grep -c '<html' index.html && echo "✓ HTML tag found"
grep -c '</html>' index.html && echo "✓ Closing HTML tag found"
grep -c '<head>' index.html && echo "✓ Head tag found"
grep -c '<body>' index.html && echo "✓ Body tag found"
