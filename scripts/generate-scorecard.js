/**
 * generate-scorecard.js
 *
 * Fetches SecurityClaw campaign results from the /scorecard API endpoint
 * and writes the result to _data/scorecard.json for 11ty to consume at
 * build time.
 *
 * Usage:
 *   node scripts/generate-scorecard.js
 *   npm run generate-scorecard
 *
 * Run before each site build to pick up new campaign results:
 *   node scripts/generate-scorecard.js && npm run build
 *
 * The SecurityClaw API URL is read from:
 *   SECURITYCLAW_API_URL  (env var) — default: http://localhost:8000
 *
 * Exported (for testing):
 *   transformApiResponse(apiResponse, categoryMeta) → scorecardData
 *   getBarClass(result) → cssClassName
 */

"use strict";

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");

// ─────────────────────────────────────────────────────────────────────────────
// Category metadata — display names and placeholder text
// ─────────────────────────────────────────────────────────────────────────────

const CATEGORY_META = {
  "secrets-detection": {
    name: "🔑 Secrets Detection",
    pending_label: "Nuclei / Nikto demos coming.",
  },
  "web-vuln-scanning": {
    name: "🌐 Web Vulnerability Scanning",
    pending_label: "Nuclei / Nikto demos in pipeline.",
  },
  "cloud-misconfiguration": {
    name: "☁️ Cloud Misconfiguration",
    pending_label: "Prowler / ScoutSuite demos in pipeline.",
  },
  "api-security": {
    name: "🔌 API Security",
    pending_label: "GraphQL / BOLA/IDOR demos in pipeline.",
  },
  "network-recon": {
    name: "📡 Network Reconnaissance",
    pending_label: "nmap / subfinder demos in pipeline.",
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Exported pure functions (used by 11ty templates + tests)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Determine the CSS class for the scorecard bar fill based on result.
 * @param {string} result - "pass" | "partial" | "fail" | "none"
 * @returns {string} CSS class name
 */
function getBarClass(result) {
  switch (result) {
    case "pass":
      return "color-green";
    case "partial":
      return "partial-stripe";
    case "fail":
      return "color-red";
    case "none":
    default:
      return "color-grey";
  }
}

/**
 * Transform the SecurityClaw GET /scorecard API response into the
 * _data/scorecard.json format that 11ty templates consume.
 *
 * @param {object} apiResponse - Response body from GET /scorecard
 * @param {object} categoryMeta - Display names + placeholder labels per category
 * @returns {object} scorecard data ready to write to _data/scorecard.json
 */
function transformApiResponse(apiResponse, categoryMeta) {
  const apiCategories = (apiResponse && apiResponse.categories) || {};
  const categories = {};

  for (const [catKey, meta] of Object.entries(categoryMeta)) {
    const apiCat = apiCategories[catKey] || null;

    if (!apiCat || !apiCat.total || apiCat.total === 0) {
      categories[catKey] = {
        name: meta.name,
        campaigns: 0,
        detection_rate: 0,
        result: "none",
        most_recent_campaign_id: null,
        most_recent_date: null,
        notes: null,
        pending_label: meta.pending_label || null,
      };
      continue;
    }

    const rate = apiCat.avg_detection_rate || 0;
    let result;
    if (rate >= 100) {
      result = "pass";
    } else if (rate > 0) {
      result = "partial";
    } else {
      result = "fail";
    }

    // If the API explicitly provides result, honour it
    if (apiCat.result && ["pass", "partial", "fail"].includes(apiCat.result)) {
      result = apiCat.result;
    }

    categories[catKey] = {
      name: meta.name,
      campaigns: apiCat.total,
      detection_rate: Math.round(rate),
      result,
      most_recent_campaign_id: apiCat.most_recent_campaign_id || null,
      most_recent_date: apiCat.most_recent_date || null,
      notes: apiCat.notes || null,
      pending_label: null,
    };
  }

  return {
    generated_at: new Date().toISOString(),
    source: "api",
    categories,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Main — fetch from API and write to _data/scorecard.json
// ─────────────────────────────────────────────────────────────────────────────

async function fetchScorecard(apiUrl) {
  const url = `${apiUrl}/scorecard`;
  const client = url.startsWith("https") ? https : http;
  return new Promise((resolve, reject) => {
    client
      .get(url, (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Failed to parse API response: ${e.message}`));
          }
        });
      })
      .on("error", reject);
  });
}

async function main() {
  const apiUrl =
    process.env.SECURITYCLAW_API_URL || "http://localhost:8000";
  const outputPath = path.join(__dirname, "..", "src", "_data", "scorecard.json");

  console.log(`🔍 Fetching scorecard from ${apiUrl}/scorecard ...`);

  try {
    const apiResponse = await fetchScorecard(apiUrl);
    const scorecard = transformApiResponse(apiResponse, CATEGORY_META);

    fs.writeFileSync(outputPath, JSON.stringify(scorecard, null, 2) + "\n");
    console.log(`✅ scorecard.json written (${Object.keys(scorecard.categories).length} categories)`);

    // Summary
    for (const [cat, data] of Object.entries(scorecard.categories)) {
      const bar =
        data.result === "none"
          ? "—"
          : `${data.detection_rate}% (${data.result})`;
      console.log(`   ${data.name}: ${bar}, ${data.campaigns} campaign(s)`);
    }
  } catch (err) {
    console.error(`❌ Failed to fetch scorecard: ${err.message}`);
    console.error(
      "   Keeping existing _data/scorecard.json (static seed will be used)"
    );
    process.exit(1);
  }
}

// Only run main when executed directly (not when required by tests)
if (require.main === module) {
  main();
}

module.exports = { transformApiResponse, getBarClass, CATEGORY_META };
