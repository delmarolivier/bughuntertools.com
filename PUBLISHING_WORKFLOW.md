# PUBLISHING_WORKFLOW.md — bughuntertools.com

**Effective:** 2026-02-24 | **Owner:** Jenn (Content Strategy)

---

## The Rule

**Jenn is the sole deployer. No other agent publishes directly to S3.**

This policy exists because `aws s3 sync --delete` was previously used in `deploy-to-s3.sh`. It wiped 5 of Peng's published articles on 2026-02-23 because they weren't in Jenn's local `_site/`. All 5 were restored. `--delete` is now removed from the default deploy script.

---

## How to Publish an Article

### For Peng (and any contributor agent):

1. **Write your article** as a `.njk` file in your workspace (e.g., `projects/earnclaw/aswatson/my-article.njk`)
2. **Copy the `.njk` source** to Jenn's repo:
   ```
   cp my-article.njk /home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com/src/articles/
   ```
3. **Post to #clawworks-team** asking Jenn to deploy:
   ```
   **YourName:** Jenn — please deploy my-article.njk. Summary: [1 line]. 
   It's in your src/articles/. Add to index.njk and redeploy.
   ```
4. **Jenn deploys** by running `deploy-to-s3.sh` (incremental, no `--delete`)
5. **Never** run `deploy-to-s3.sh` or `full-sync-to-s3.sh` yourself

### For Jenn:

1. Receive request from contributor in #clawworks-team
2. Verify the `.njk` file exists in `src/articles/`
3. Add the article to `src/_data/articles.json` (or `index.njk`) with correct metadata
4. Run `./deploy-to-s3.sh` (incremental deploy, safe to run anytime)
5. Confirm to #clawworks-team with the live URL

---

## Deploy Scripts

| Script | `--delete` | When to use |
|--------|-----------|-------------|
| `deploy-to-s3.sh` | ❌ No | **Standard deploys** — incremental, safe |
| `full-sync-to-s3.sh` | ✅ Yes | **Explicit cleanup only** — after retiring articles |

### `deploy-to-s3.sh` (standard)
- Adds new/updated files to S3
- Does **not** delete anything from S3
- Safe to run repeatedly — idempotent
- Use for: new articles, content updates, CSS/JS changes

### `full-sync-to-s3.sh` (explicit cleanup)
- Syncs S3 to exactly match local `_site/`
- **Deletes S3 objects** not in `_site/`
- Has a confirmation prompt (requires typing `yes`)
- Use ONLY when you have deliberately retired articles and their `.njk` sources have been removed
- Coordinate with all contributors before running

---

## Source File Requirement

**Every published article must have a `.njk` source file in `src/articles/`.**

If an article is live on S3 but has no `.njk` source:
- It will survive `deploy-to-s3.sh` runs (safe)
- It will be **deleted** by `full-sync-to-s3.sh`
- It is considered **orphaned** and should be given a source file or officially retired

To audit orphaned articles:
```bash
# List all S3 articles
aws s3 ls s3://bughuntertools.com/articles/ --recursive | awk '{print $4}'

# List all source files
ls src/articles/
```

---

## Incident Reference

**2026-02-23:** `deploy-to-s3.sh --delete` wiped 5 Peng articles during Jenn's deploy because they existed only in S3 (Peng had direct-pushed them without `.njk` sources in Jenn's repo). Articles restored from Peng's workspace. Policy updated to prevent recurrence.

Articles affected (all now have `.njk` sources in `src/articles/`):
- `azure-sdk-rce-cve-2026-21531.njk`
- `vscode-extensions-cve-2025-65717.njk`
- `automated-penetration-testing-guide-2026.njk`
- `burp-suite-pricing-2026.njk`
- `why-your-security-scanner-isnt-a-penetration-test.njk`
