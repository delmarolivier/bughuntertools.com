# AltClaw Automation Fix - TDD Approach

**Date:** 2026-02-10  
**Issue:** Breaking news articles created in wrong format, not building/deploying  
**Resolution:** Fixed via Test-Driven Development

## Problem

Daily research cron job spawned sub-agents that created complete HTML files in `articles/` directory. Site migrated to 11ty on Feb 8 but automation instructions never updated.

**Result:** vLLM article (CVE-2026-22778) written but never deployed properly.

## TDD Solution

### 1. Write Tests First (`tests/test_article_workflow.py`)

Created comprehensive test suite covering:
- ✅ Article template location (must be `src/articles/*.njk`)
- ✅ Template structure (frontmatter + content, no `<html>/<head>/<body>`)
- ✅ 11ty build process (templates → HTML)
- ✅ Article index updated
- ✅ Sitemap generation
- ✅ **Breaking news format** (the failing test)
- ✅ Deployment readiness

**Initial run:** 6 passed, 1 failed (breaking news format)

### 2. Fix the Code

**Updated cron job payload with:**
- Explicit 11ty instructions
- Correct file location: `src/articles/TOPIC-SLUG.njk`
- Proper template structure (frontmatter + article content)
- Reference to existing template (n8n article)
- Build + test + deploy workflow
- Git commit requirement

**Converted vLLM article:**
- Moved to `src/articles/vllm-rce-cve-2026-22778.njk`
- Stripped HTML boilerplate
- Added proper frontmatter
- Updated article index

### 3. Verify Tests Pass

**Final run:** 7 passed, 0 failed ✅

### 4. Deploy

- Built with 11ty
- Deployed to S3
- Verified live at https://bughuntertools.com/articles/vllm-rce-cve-2026-22778.html
- Committed to git

## Test Results

```
AltClaw Article Workflow Tests (TDD)
============================================================

test_article_template_location:
✓ Found 8 article templates in correct location

test_article_template_structure:
✓ Article template has correct structure (frontmatter + content)

test_article_builds_to_html:
✓ 11ty builds templates to proper HTML with layout

test_article_index_updated:
✓ Article index exists

test_sitemap_generation:
✓ Sitemap includes articles

test_breaking_news_article_format:
✓ Breaking news article in correct format

test_article_deployment_ready:
✓ 8 articles ready for deployment

============================================================
Results: 7 passed, 0 failed
============================================================
```

## What Changed

### Cron Job Instructions (Daily Research)

**Before:** Vague "follow format from articles/linkedin-api-bola-bypass.html"
**After:** Explicit template structure, file location, build steps, test verification

**Key additions:**
```
CRITICAL: Site uses 11ty static site generator with Nunjucks templates.

REQUIRED FORMAT:
- Create file: projects/altclaw/bughuntertools.com/src/articles/TOPIC-SLUG.njk
- NOT .html, must be .njk template
- NOT in articles/ directory, must be in src/articles/

TEMPLATE STRUCTURE:
---
title: 'Article Title Here'
description: Brief 1-2 sentence description
layout: base.njk
permalink: /articles/TOPIC-SLUG.html
---

<article>
[Content - NO <html>, <head>, <body> tags]
</article>

After creating template:
1. Update src/articles/index.njk
2. Run: npx @11ty/eleventy
3. Run: python3 tests/test_article_workflow.py
4. Run: ./deploy-to-s3.sh
5. Git commit and push
```

### Test Suite

**Location:** `projects/altclaw/tests/test_article_workflow.py`

**Purpose:** Prevent regression - ensures future articles follow correct format

**Run before every deployment:** Catches format issues before they reach production

## Prevention

**Future breaking news articles will:**
1. Create proper `.njk` templates
2. Place files in correct location
3. Run test suite
4. Pass all 7 tests
5. Deploy successfully

**No more manual fixes required.**

## Validation

✅ vLLM article now live and properly formatted  
✅ All tests pass  
✅ Cron job updated with correct instructions  
✅ Test suite prevents future regressions  
✅ Changes committed to git  

**TDD worked:** Tests defined expected behavior, code fixed to match, tests confirm success.
