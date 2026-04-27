import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://bughuntertools.com',
  integrations: [
    sitemap(),
  ],
  build: {
    // Keep trailing slashes consistent
  },
  trailingSlash: 'always',
  // Astro outputs to dist/ by default
});
