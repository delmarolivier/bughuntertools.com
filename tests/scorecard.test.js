/**
 * TDD tests for SecurityClaw Demos Scorecard dynamic data pipeline.
 *
 * Tests written BEFORE implementation (red → green).
 *
 * Tests cover:
 * 1. _data/scorecard.json schema validation
 * 2. Seed data correctness (TruffleHog v3 100% result)
 * 3. generate-scorecard.js: API response → scorecard.json transformation
 * 4. Category bar CSS class selection logic
 */

const fs = require("fs");
const path = require("path");

const SCORECARD_DATA_PATH = path.join(
  __dirname,
  "..",
  "src",
  "_data",
  "scorecard.json"
);
const GENERATE_SCRIPT_PATH = path.join(
  __dirname,
  "..",
  "scripts",
  "generate-scorecard.js"
);

// ─────────────────────────────────────────────────────────────────────────────
// 1. _data/scorecard.json schema
// ─────────────────────────────────────────────────────────────────────────────

describe("scorecard.json schema", () => {
  let scorecard;

  beforeAll(() => {
    scorecard = JSON.parse(fs.readFileSync(SCORECARD_DATA_PATH, "utf8"));
  });

  test("has generated_at timestamp", () => {
    expect(scorecard.generated_at).toBeDefined();
    expect(new Date(scorecard.generated_at).getFullYear()).toBeGreaterThanOrEqual(
      2026
    );
  });

  test("has categories object", () => {
    expect(scorecard.categories).toBeDefined();
    expect(typeof scorecard.categories).toBe("object");
  });

  test("has all 5 required categories", () => {
    const required = [
      "secrets-detection",
      "web-vuln-scanning",
      "cloud-misconfiguration",
      "api-security",
      "network-recon",
    ];
    required.forEach((cat) => {
      expect(scorecard.categories).toHaveProperty(
        cat,
        expect.objectContaining({ name: expect.any(String) })
      );
    });
  });

  test("each category has required fields", () => {
    Object.entries(scorecard.categories).forEach(([key, cat]) => {
      expect(cat).toHaveProperty("name");
      expect(cat).toHaveProperty("campaigns");
      expect(typeof cat.campaigns).toBe("number");
      expect(cat).toHaveProperty("detection_rate");
      expect(typeof cat.detection_rate).toBe("number");
      expect(cat.detection_rate).toBeGreaterThanOrEqual(0);
      expect(cat.detection_rate).toBeLessThanOrEqual(100);
      expect(cat).toHaveProperty("result");
      expect(["pass", "partial", "fail", "none"]).toContain(cat.result);
    });
  });

  test("categories with 0 campaigns have result=none and detection_rate=0", () => {
    Object.values(scorecard.categories).forEach((cat) => {
      if (cat.campaigns === 0) {
        expect(cat.result).toBe("none");
        expect(cat.detection_rate).toBe(0);
      }
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 2. Seed data correctness — TruffleHog v3 demo result
// ─────────────────────────────────────────────────────────────────────────────

describe("scorecard seed data — TruffleHog demo", () => {
  let scorecard;

  beforeAll(() => {
    scorecard = JSON.parse(fs.readFileSync(SCORECARD_DATA_PATH, "utf8"));
  });

  test("secrets-detection has 1 campaign", () => {
    expect(scorecard.categories["secrets-detection"].campaigns).toBe(1);
  });

  test("secrets-detection detection_rate is 100 (v3 full pass)", () => {
    // TruffleHog v3.93.4 detected 5/5 secrets — 100%
    expect(scorecard.categories["secrets-detection"].detection_rate).toBe(100);
  });

  test("secrets-detection result is pass", () => {
    expect(scorecard.categories["secrets-detection"].result).toBe("pass");
  });

  test("secrets-detection has notes about TruffleHog", () => {
    const cat = scorecard.categories["secrets-detection"];
    expect(cat.notes).toBeDefined();
    expect(cat.notes.toLowerCase()).toMatch(/trufflehog/i);
  });

  test("secrets-detection has most_recent_campaign_id", () => {
    const cat = scorecard.categories["secrets-detection"];
    expect(cat.most_recent_campaign_id).toBeDefined();
    expect(typeof cat.most_recent_campaign_id).toBe("string");
  });

  test("all other categories have 0 campaigns", () => {
    const pending = [
      "web-vuln-scanning",
      "cloud-misconfiguration",
      "api-security",
      "network-recon",
    ];
    pending.forEach((cat) => {
      expect(scorecard.categories[cat].campaigns).toBe(0);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 3. generate-scorecard.js transformation logic
// ─────────────────────────────────────────────────────────────────────────────

describe("generate-scorecard.js API response transformation", () => {
  let transformApiResponse;

  beforeAll(() => {
    // Require only the transform function — avoids side effects of the full script
    const mod = require(GENERATE_SCRIPT_PATH);
    transformApiResponse = mod.transformApiResponse;
  });

  const CATEGORY_META = {
    "secrets-detection": {
      name: "🔑 Secrets Detection",
      pending_label: "Nuclei / Nikto demos coming",
    },
    "web-vuln-scanning": {
      name: "🌐 Web Vulnerability Scanning",
      pending_label: "Nuclei / Nikto demos coming",
    },
    "cloud-misconfiguration": {
      name: "☁️ Cloud Misconfiguration",
      pending_label: "Prowler / ScoutSuite demos coming",
    },
    "api-security": {
      name: "🔌 API Security",
      pending_label: "GraphQL / BOLA/IDOR demos coming",
    },
    "network-recon": {
      name: "📡 Network Reconnaissance",
      pending_label: "nmap / subfinder demos coming",
    },
  };

  test("transforms empty API response to all-none scorecard", () => {
    const apiResponse = { categories: {} };
    const result = transformApiResponse(apiResponse, CATEGORY_META);
    expect(result.categories["secrets-detection"].result).toBe("none");
    expect(result.categories["secrets-detection"].campaigns).toBe(0);
  });

  test("transforms single pass result correctly", () => {
    const apiResponse = {
      categories: {
        "secrets-detection": {
          pass: 1,
          partial: 0,
          fail: 0,
          total: 1,
          avg_detection_rate: 100,
          most_recent_campaign_id: "demo-trufflehog-001",
        },
      },
    };
    const result = transformApiResponse(apiResponse, CATEGORY_META);
    const cat = result.categories["secrets-detection"];
    expect(cat.campaigns).toBe(1);
    expect(cat.detection_rate).toBe(100);
    expect(cat.result).toBe("pass");
    expect(cat.name).toBe("🔑 Secrets Detection");
  });

  test("partial result when avg_detection_rate < 100 and > 0", () => {
    const apiResponse = {
      categories: {
        "secrets-detection": {
          pass: 0,
          partial: 1,
          fail: 0,
          total: 1,
          avg_detection_rate: 80,
          most_recent_campaign_id: "demo-trufflehog-001",
        },
      },
    };
    const result = transformApiResponse(apiResponse, CATEGORY_META);
    const cat = result.categories["secrets-detection"];
    expect(cat.result).toBe("partial");
    expect(cat.detection_rate).toBe(80);
  });

  test("fail result when avg_detection_rate is 0", () => {
    const apiResponse = {
      categories: {
        "network-recon": {
          pass: 0,
          partial: 0,
          fail: 1,
          total: 1,
          avg_detection_rate: 0,
          most_recent_campaign_id: "demo-nmap-001",
        },
      },
    };
    const result = transformApiResponse(apiResponse, CATEGORY_META);
    expect(result.categories["network-recon"].result).toBe("fail");
  });

  test("result has generated_at timestamp", () => {
    const result = transformApiResponse({ categories: {} }, CATEGORY_META);
    expect(result.generated_at).toBeDefined();
    expect(new Date(result.generated_at).toString()).not.toBe("Invalid Date");
  });

  test("missing categories in API response default to none", () => {
    const apiResponse = {
      categories: {
        "secrets-detection": {
          pass: 1,
          partial: 0,
          fail: 0,
          total: 1,
          avg_detection_rate: 100,
          most_recent_campaign_id: "demo-001",
        },
      },
    };
    const result = transformApiResponse(apiResponse, CATEGORY_META);
    // Other categories not in API response default to none
    expect(result.categories["api-security"].campaigns).toBe(0);
    expect(result.categories["api-security"].result).toBe("none");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 4. CSS class selection logic
// ─────────────────────────────────────────────────────────────────────────────

describe("scorecard bar CSS class selection", () => {
  let getBarClass;

  beforeAll(() => {
    const mod = require(GENERATE_SCRIPT_PATH);
    getBarClass = mod.getBarClass;
  });

  test("pass → color-green", () => {
    expect(getBarClass("pass")).toBe("color-green");
  });

  test("partial → partial-stripe", () => {
    expect(getBarClass("partial")).toBe("partial-stripe");
  });

  test("fail → color-red", () => {
    expect(getBarClass("fail")).toBe("color-red");
  });

  test("none → color-grey", () => {
    expect(getBarClass("none")).toBe("color-grey");
  });

  test("unknown → color-grey (fallback)", () => {
    expect(getBarClass("unknown")).toBe("color-grey");
  });
});
