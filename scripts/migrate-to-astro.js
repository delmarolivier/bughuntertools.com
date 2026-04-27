#!/usr/bin/env node
/**
 * Migrate 11ty Nunjucks articles to Astro pages
 * Usage: node scripts/migrate-to-astro.js
 */

const fs = require('fs');
const path = require('path');

const ARTICLES_SRC = path.join(__dirname, '../src/articles');
const ARTICLES_DEST = path.join(__dirname, '../src/pages/articles');

// Parse YAML-ish frontmatter (simple key: value pairs only)
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { fm: {}, body: content };

  const fmLines = match[1];
  const body = match[2];
  const fm = {};

  for (const line of fmLines.split('\n')) {
    const m = line.match(/^(\w+):\s*(.*)$/);
    if (m) {
      let val = m[2].trim().replace(/^['"]|['"]$/g, '');
      fm[m[1]] = val;
    }
  }

  return { fm, body };
}

// Escape backticks and template literals in HTML for use in Astro template
function escapeForAstro(html) {
  // No escaping needed — we'll use set:html directive for the content
  return html.trim();
}

function migrateArticle(srcFile) {
  const slug = path.basename(srcFile, '.njk');
  if (slug === 'index') return null;

  const raw = fs.readFileSync(srcFile, 'utf8');
  const { fm, body } = parseFrontmatter(raw);

  const title = (fm.title || slug).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  const description = (fm.description || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  const date = fm.date || '';

  // Strip Nunjucks tags from body
  let cleanBody = body
    .replace(/\{%[\s\S]*?%\}/g, '')
    .replace(/\{\{[^}]*\}\}/g, '')
    .trim();

  // Escape for JS template literal: backticks and template expressions
  const escapedHtml = cleanBody
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$\{/g, '\\${');

  // Create directory for the article
  const destDir = path.join(ARTICLES_DEST, slug);
  fs.mkdirSync(destDir, { recursive: true });

  // Write Astro page using set:html to safely inject raw HTML
  const astroContent = `---
import BaseLayout from '../../../layouts/BaseLayout.astro';

const title = '${title}';
const description = '${description}';
const date = '${date}';
const html = \`${escapedHtml}\`;
---
<BaseLayout title={title} description={description} isArticle={true} schemaType="Article">
  <Fragment set:html={html} />
</BaseLayout>
`;

  const destFile = path.join(destDir, 'index.astro');
  fs.writeFileSync(destFile, astroContent, 'utf8');
  return slug;
}

// Run migration
let migrated = 0;
let failed = 0;

const files = fs.readdirSync(ARTICLES_SRC)
  .filter(f => f.endsWith('.njk') && !f.endsWith('.backup') && !f.includes('.backup'))
  .filter(f => f !== 'index.njk');

console.log(`Found ${files.length} article files to migrate`);

for (const file of files) {
  const srcFile = path.join(ARTICLES_SRC, file);
  try {
    const slug = migrateArticle(srcFile);
    if (slug) {
      console.log(`  ✓ ${slug}`);
      migrated++;
    }
  } catch (err) {
    console.error(`  ✗ ${file}: ${err.message}`);
    failed++;
  }
}

console.log(`\nMigration complete: ${migrated} migrated, ${failed} failed`);
