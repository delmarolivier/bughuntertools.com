#!/usr/bin/env python3
"""
Test article creation workflow for AltClaw breaking news automation.

TDD: These tests define the expected behavior before implementation.
"""

import os
import re
import json
from pathlib import Path

# Test data
WORKSPACE = Path("/home/delmar/.openclaw/workspace")
SITE_DIR = WORKSPACE / "projects/altclaw/bughuntertools.com"
SRC_ARTICLES = SITE_DIR / "src/articles"
BUILD_DIR = SITE_DIR / "_site/articles"


def test_article_template_location():
    """Test: Articles must be created in src/articles/ as .njk files"""
    # This is where 11ty looks for source files
    assert SRC_ARTICLES.exists(), f"Source directory missing: {SRC_ARTICLES}"
    
    # All article templates should be .njk files
    templates = list(SRC_ARTICLES.glob("*.njk"))
    assert len(templates) > 0, "No article templates found"
    
    print(f"✓ Found {len(templates)} article templates in correct location")


def test_article_template_structure():
    """Test: Article templates must have proper frontmatter"""
    sample = SRC_ARTICLES / "n8n-rce-cve-2026-21858.njk"
    assert sample.exists(), f"Sample template missing: {sample}"
    
    content = sample.read_text()
    
    # Must have frontmatter delimiters
    assert content.startswith("---\n"), "Template must start with frontmatter"
    assert "\n---\n" in content, "Template must have closing frontmatter delimiter"
    
    # Extract frontmatter
    parts = content.split("---\n", 2)
    assert len(parts) >= 3, "Invalid frontmatter structure"
    
    frontmatter = parts[1]
    
    # Required frontmatter fields
    assert "title:" in frontmatter, "Missing required field: title"
    assert "description:" in frontmatter, "Missing required field: description"
    assert "layout: base.njk" in frontmatter, "Missing required field: layout"
    assert "permalink:" in frontmatter, "Missing required field: permalink"
    
    # Article content (after frontmatter) should NOT have <html>, <head>, <body>
    article_content = parts[2]
    assert "<html" not in article_content.lower(), "Template should not contain <html> tag"
    assert "<head" not in article_content.lower(), "Template should not contain <head> tag"
    assert "<body" not in article_content.lower(), "Template should not contain <body> tag"
    assert article_content.strip().startswith("<article>"), "Content should start with <article>"
    
    print("✓ Article template has correct structure (frontmatter + content)")


def test_article_builds_to_html():
    """Test: 11ty must build .njk templates to .html files"""
    # After running `npx @11ty/eleventy`, _site should have built HTML
    assert BUILD_DIR.exists(), f"Build directory missing: {BUILD_DIR}"
    
    html_files = list(BUILD_DIR.glob("*.html"))
    assert len(html_files) > 0, "No HTML files built"
    
    # Built files should have proper HTML structure with layout applied
    sample_html = BUILD_DIR / "n8n-rce-cve-2026-21858.html"
    if sample_html.exists():
        content = sample_html.read_text()
        assert "<!DOCTYPE html>" in content, "Built HTML missing DOCTYPE"
        assert "<html" in content, "Built HTML missing <html> tag"
        assert "<head>" in content, "Built HTML missing <head> tag"
        assert "<body>" in content, "Built HTML missing <body> tag"
        print("✓ 11ty builds templates to proper HTML with layout")
    else:
        print("⚠ Skipping build validation (run 11ty first)")


def test_article_index_updated():
    """Test: articles/index.njk must list all articles"""
    index_path = SRC_ARTICLES / "index.njk"
    assert index_path.exists(), f"Article index missing: {index_path}"
    
    # Index should reference other articles
    index_content = index_path.read_text()
    assert "bug-bounty-starter-kit" in index_content, "Index should list articles"
    
    print("✓ Article index exists")


def test_sitemap_generation():
    """Test: sitemap.xml must include all articles"""
    sitemap = SITE_DIR / "_site/sitemap.xml"
    
    if sitemap.exists():
        content = sitemap.read_text()
        assert "bughuntertools.com/articles/" in content, "Sitemap should include article URLs"
        print("✓ Sitemap includes articles")
    else:
        print("⚠ Sitemap not found (run build first)")


def test_breaking_news_article_format():
    """
    Test: Breaking news articles created by automation must match expected format.
    This is the KEY test that the current automation fails.
    """
    # Expected: vllm article should be a .njk template in src/articles/
    expected_template = SRC_ARTICLES / "vllm-rce-cve-2026-22778.njk"
    
    # Current bug: Article was created as HTML in wrong location
    wrong_location = SITE_DIR / "articles/vllm-rce-cve-2026-22778.html"
    
    if wrong_location.exists() and not expected_template.exists():
        raise AssertionError(
            f"FAIL: Article created in wrong location!\n"
            f"  Found: {wrong_location}\n"
            f"  Expected: {expected_template}\n"
            f"  Article must be .njk template in src/articles/, not HTML in articles/"
        )
    
    if expected_template.exists():
        content = expected_template.read_text()
        assert content.startswith("---\n"), "Breaking news article must have frontmatter"
        assert "<html" not in content.lower(), "Breaking news article should be template, not complete HTML"
        print("✓ Breaking news article in correct format")
    else:
        print("⚠ Breaking news article not found (run automation first)")


def test_article_deployment_ready():
    """Test: After build, articles must be ready for S3 deployment"""
    if BUILD_DIR.exists():
        html_files = list(BUILD_DIR.glob("*.html"))
        for html_file in html_files:
            content = html_file.read_text()
            # Should have complete HTML structure
            assert "<!DOCTYPE html>" in content
            assert "</html>" in content
            # Should have CSS reference
            assert "/css/style.css" in content
            
        print(f"✓ {len(html_files)} articles ready for deployment")
    else:
        print("⚠ Build directory not found")


if __name__ == "__main__":
    print("=" * 60)
    print("AltClaw Article Workflow Tests (TDD)")
    print("=" * 60)
    
    tests = [
        test_article_template_location,
        test_article_template_structure,
        test_article_builds_to_html,
        test_article_index_updated,
        test_sitemap_generation,
        test_breaking_news_article_format,  # This should FAIL currently
        test_article_deployment_ready,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    exit(0 if failed == 0 else 1)
