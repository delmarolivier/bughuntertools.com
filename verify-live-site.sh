#!/bin/bash

# Post-deployment live site verification
# Tests the actual deployed site, not just local files

SITE="https://bughuntertools.com"

echo "=== Live Site Verification ==="
echo ""

# Test 1: All pages load with 200
echo "1. Testing page availability..."
PAGES=(
    "/"
    "/articles/"
    "/articles/security-testing-tools-2026.html"
    "/articles/bug-bounty-starter-kit.html"
    "/privacy.html"
)

for page in "${PAGES[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SITE$page")
    if [ "$STATUS" = "200" ]; then
        echo "✓ $page"
    else
        echo "✗ $page (HTTP $STATUS)"
        exit 1
    fi
done
echo ""

# Test 2: Critical links work
echo "2. Testing critical links..."
# Browse All Articles button on homepage
if curl -s "$SITE/" | grep -q 'href="/articles/".*Browse All Articles'; then
    echo "✓ Homepage → Articles link present"
else
    echo "✗ Homepage → Articles link missing or wrong"
    exit 1
fi

# Navigation on all pages
if curl -s "$SITE/" | grep -q 'class="main-nav"'; then
    echo "✓ Navigation present on homepage"
else
    echo "✗ Navigation missing on homepage"
    exit 1
fi
echo ""

# Test 3: Navigation highlighting
echo "3. Testing navigation highlighting..."
# Home page should highlight Home
if curl -s "$SITE/" | grep -A5 "main-nav" | grep -q 'href="/".*rgba.*>Home'; then
    echo "✓ Home page highlights Home"
else
    echo "✗ Home page doesn't highlight Home correctly"
fi

# Articles page should highlight Articles
if curl -s "$SITE/articles/" | grep -A5 "main-nav" | grep -q 'href="/articles/".*rgba.*>Articles'; then
    echo "✓ Articles page highlights Articles"
else
    echo "✗ Articles page doesn't highlight Articles correctly"
fi

# Tools page should highlight Tools
if curl -s "$SITE/articles/security-testing-tools-2026.html" | grep -A5 "main-nav" | grep -q 'security-testing-tools.*rgba.*>Tools'; then
    echo "✓ Tools page highlights Tools"
else
    echo "✗ Tools page doesn't highlight Tools correctly"
fi
echo ""

# Test 4: Key content present
echo "4. Testing key content..."
if curl -s "$SITE/" | grep -q "Optimized for AI Agents"; then
    echo "✓ Homepage has AI optimization message"
else
    echo "✗ Homepage missing AI optimization message"
fi

if curl -s "$SITE/articles/" | grep -q "All Bug Bounty"; then
    echo "✓ Articles index has content"
else
    echo "✗ Articles index missing content"
fi
echo ""

echo "✅ Live site verification complete!"
