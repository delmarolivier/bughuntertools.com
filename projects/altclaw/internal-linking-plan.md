# Internal Linking Strategy - AltClaw

## Article Categories & Related Links

### AI/ML Security Articles
- **vllm-rce-cve-2026-22778**
  - Related: chainlit-ai-vulnerabilities-cve-2026-22218, security-testing-tools-2026
  
- **chainlit-ai-vulnerabilities-cve-2026-22218**
  - Related: vllm-rce-cve-2026-22778, n8n-rce-cve-2026-25049

### Workflow Automation Security
- **n8n-rce-cve-2026-21858**
  - Related: n8n-rce-cve-2026-25049, chainlit-ai-vulnerabilities-cve-2026-22218
  
- **n8n-rce-cve-2026-25049**
  - Related: n8n-rce-cve-2026-21858, linkedin-api-bola-bypass
  
- **linkedin-api-bola-bypass**
  - Related: n8n-rce-cve-2026-25049, security-testing-tools-2026

### Microsoft/Windows Security
- **microsoft-patch-tuesday-february-2026-zero-days**
  - Related: mshtml-cve-2026-21513, adobe-after-effects-cve-2026-21329
  
- **mshtml-cve-2026-21513**
  - Related: microsoft-patch-tuesday-february-2026-zero-days, adobe-after-effects-cve-2026-21329
  
- **adobe-after-effects-cve-2026-21329**
  - Related: microsoft-patch-tuesday-february-2026-zero-days, mshtml-cve-2026-21513

### Educational/Reference Guides
- **bug-bounty-starter-kit**
  - Related: security-lab-setup-guide-2026, security-testing-tools-2026
  
- **security-lab-setup-guide-2026**
  - Related: bug-bounty-starter-kit, security-testing-tools-2026
  
- **security-testing-tools-2026**
  - Related: bug-bounty-starter-kit, security-lab-setup-guide-2026

## Implementation Plan

**Phase 1: Create Reusable Component**
- Create `src/_includes/related-articles.njk` component
- Pass article slug and related articles as parameters
- Style with CSS (card layout, hover effects)

**Phase 2: Add to Each Article**
- Add related articles data to front matter
- Include component before closing article tag
- Test rendering

**Phase 3: Deploy & Verify**
- Build, sync S3, invalidate CloudFront
- Verify links work correctly
- Check styling on mobile

## Expected Impact
- Reduces bounce rate by 10-15%
- Increases pages per session by 30-50%
- Improves SEO (internal link equity distribution)
- Better user engagement (content discovery)
