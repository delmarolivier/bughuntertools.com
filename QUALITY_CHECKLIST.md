# Post-Commit Quality Checklist

**MANDATORY before every commit to production sites**

## Pre-Deployment Checks

### 1. Link Validation
- [ ] No `href="#"` placeholder links
- [ ] All external links have valid URLs
- [ ] Links open in new tab where appropriate (`target="_blank"`)
- [ ] All internal anchor links point to existing IDs

### 2. Content Quality
- [ ] No Lorem Ipsum or placeholder text
- [ ] Spelling and grammar checked
- [ ] All CTAs have actionable text
- [ ] Contact information is accurate

### 3. SEO & Metadata
- [ ] `<title>` tag present and descriptive
- [ ] Meta description present (150-160 chars)
- [ ] Schema.org markup for AI optimization
- [ ] Open Graph tags for social sharing (optional)

### 4. Performance
- [ ] Images optimized and have alt tags
- [ ] CSS/JS minified (if applicable)
- [ ] No broken images or missing assets
- [ ] File sizes reasonable (<100KB for HTML)

### 5. Functionality
- [ ] Forms work (if present)
- [ ] Navigation works on mobile
- [ ] All sections/anchors accessible
- [ ] No console errors (check in browser)

### 6. Legal/Compliance
- [ ] Privacy policy link (if collecting data)
- [ ] Disclaimer present (if giving advice)
- [ ] Affiliate disclosures (FTC compliance)
- [ ] Copyright notice in footer

## Automated Check

Run before every commit:
```bash
./check-quality.sh
```

Review output and fix any issues before pushing.

## Manual Testing

After deployment:
1. Open site in browser
2. Click every link
3. Test on mobile (Chrome DevTools)
4. Check console for errors (F12)
5. Validate HTML: validator.w3.org

## Lesson Learned (2026-02-08)

**Mistake:** Shipped site with placeholder `href="#"` links  
**Impact:** Broken user experience, unprofessional  
**Root cause:** Skipped quality check before deployment  
**Fix:** Created this checklist and automated script  
**Prevention:** ALWAYS run check-quality.sh before git push

---

**Remember:** Shipping fast is good. Shipping broken is not. 2 minutes of checking saves 20 minutes of fixing.
