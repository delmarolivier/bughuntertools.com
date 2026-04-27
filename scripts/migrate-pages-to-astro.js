#!/usr/bin/env node
/**
 * Migrate remaining 11ty pages (non-article) to Astro
 * Handles: articles/index, privacy, securityclaw, demos/index, demos/trufflehog
 */

const fs = require('fs');
const path = require('path');

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { fm: {}, body: content };

  const fmLines = match[1];
  const body = match[2];
  const fm = {};

  for (const line of fmLines.split('\n')) {
    const m = line.match(/^(\w[\w-]*):\s*(.*)$/);
    if (m) {
      let val = m[2].trim().replace(/^['"]|['"]$/g, '');
      fm[m[1]] = val;
    }
  }

  return { fm, body };
}

function escapeStr(s) {
  return (s || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

function buildAstroPage(fm, body, layoutDepth) {
  const dots = '../'.repeat(layoutDepth);
  const title = escapeStr(fm.title || 'Bug Hunter Tools');
  const description = escapeStr(fm.description || '');

  // Escape for JS template literal
  const escapedHtml = body
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$\{/g, '\\${');

  return `---
import BaseLayout from '${dots}layouts/BaseLayout.astro';

const title = '${title}';
const description = '${description}';
const html = \`${escapedHtml}\`;
---
<BaseLayout title={title} description={description}>
  <Fragment set:html={html} />
</BaseLayout>
`;
}

const pages = [
  // [srcFile, destFile, layoutDepth]
  ['src/articles/index.njk', 'src/pages/articles/index.astro', 2],
  ['src/privacy.njk', 'src/pages/privacy/index.astro', 2],
  ['src/securityclaw.njk', 'src/pages/securityclaw/index.astro', 2],
  ['src/demos/index.njk', 'src/pages/demos/index.astro', 2],
  ['src/demos/trufflehog-secrets-detection-demo-2026.njk', 'src/pages/demos/trufflehog-secrets-detection-demo-2026/index.astro', 3],
];

const root = path.join(__dirname, '..');

let ok = 0;
for (const [src, dest, depth] of pages) {
  const srcPath = path.join(root, src);
  const destPath = path.join(root, dest);
  try {
    const raw = fs.readFileSync(srcPath, 'utf8');
    const { fm, body } = parseFrontmatter(raw);
    // Strip nunjucks conditionals / includes from body (replace with empty)
    let cleanBody = body
      .replace(/\{%[^%]*%\}/g, '')  // remove nunjucks tags
      .replace(/\{\{[^}]*\}\}/g, '') // remove nunjucks expressions
      .trim();
    const astro = buildAstroPage(fm, cleanBody, depth);
    fs.mkdirSync(path.dirname(destPath), { recursive: true });
    fs.writeFileSync(destPath, astro, 'utf8');
    console.log(`  ✓ ${src} → ${dest}`);
    ok++;
  } catch (err) {
    console.error(`  ✗ ${src}: ${err.message}`);
  }
}

console.log(`\nDone: ${ok}/${pages.length} pages migrated`);
