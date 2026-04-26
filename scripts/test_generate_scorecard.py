"""
TDD tests for generate_scorecard.py
Tests written BEFORE implementation.

Validates scorecard data generation from SecurityClaw campaigns.db
for publishing to bughuntertools.com _data/securityclaw_scorecard.json
"""
import json
import os
import sqlite3
import tempfile
from pathlib import Path
import pytest

from generate_scorecard import (
    generate_scorecard,
    calculate_category_stats,
    build_output,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

def make_db(rows: list) -> str:
    """Create a temp campaigns.db with given rows. Returns db path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    conn = sqlite3.connect(tmp.name)
    conn.execute("""
        CREATE TABLE campaign_results (
            id INTEGER PRIMARY KEY,
            campaign_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            tool TEXT NOT NULL,
            category TEXT NOT NULL,
            result TEXT NOT NULL,
            notes TEXT,
            timing_seconds REAL,
            planted_count INTEGER,
            found_count INTEGER,
            false_positives INTEGER,
            ai_gap_fill INTEGER DEFAULT 0,
            target_type TEXT,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            demo_article_url TEXT
        )
    """)
    for row in rows:
        conn.execute(
            "INSERT INTO campaign_results (campaign_id, date, tool, category, result) VALUES (?,?,?,?,?)",
            row
        )
    conn.commit()
    conn.close()
    return tmp.name


# ── calculate_category_stats tests ─────────────────────────────────────────

class TestCalculateCategoryStats:
    def test_empty_list_returns_empty_dict(self):
        result = calculate_category_stats([])
        assert result == {}

    def test_single_pass_result(self):
        rows = [{"category": "web-scanning", "result": "pass", "tool": "nuclei"}]
        result = calculate_category_stats(rows)
        assert "web-scanning" in result
        cat = result["web-scanning"]
        assert cat["campaigns_run"] == 1
        assert cat["pass_rate"] == 1.0
        assert cat["fail_rate"] == 0.0
        assert cat["partial_rate"] == 0.0
        assert "nuclei" in cat["tools"]

    def test_mixed_results_calculates_rates(self):
        rows = [
            {"category": "web-scanning", "result": "pass", "tool": "nuclei"},
            {"category": "web-scanning", "result": "pass", "tool": "nikto"},
            {"category": "web-scanning", "result": "fail", "tool": "nuclei"},
            {"category": "web-scanning", "result": "partial", "tool": "wpscan"},
        ]
        result = calculate_category_stats(rows)
        cat = result["web-scanning"]
        assert cat["campaigns_run"] == 4
        assert cat["pass_rate"] == pytest.approx(0.5)
        assert cat["fail_rate"] == pytest.approx(0.25)
        assert cat["partial_rate"] == pytest.approx(0.25)

    def test_multiple_categories_are_separate(self):
        rows = [
            {"category": "web-scanning", "result": "pass", "tool": "nuclei"},
            {"category": "secrets-detection", "result": "pass", "tool": "trufflehog"},
            {"category": "secrets-detection", "result": "fail", "tool": "trufflehog"},
        ]
        result = calculate_category_stats(rows)
        assert len(result) == 2
        assert result["web-scanning"]["campaigns_run"] == 1
        assert result["secrets-detection"]["campaigns_run"] == 2

    def test_tool_list_is_deduplicated(self):
        rows = [
            {"category": "web-scanning", "result": "pass", "tool": "nuclei"},
            {"category": "web-scanning", "result": "pass", "tool": "nuclei"},
            {"category": "web-scanning", "result": "pass", "tool": "nikto"},
        ]
        result = calculate_category_stats(rows)
        cat = result["web-scanning"]
        assert len(cat["tools"]) == 2
        assert "nuclei" in cat["tools"]
        assert "nikto" in cat["tools"]

    def test_rates_are_rounded_to_2_decimal_places(self):
        rows = [{"category": "web-scanning", "result": r, "tool": "t"} for r in ["pass"] * 1 + ["fail"] * 2]
        result = calculate_category_stats(rows)
        cat = result["web-scanning"]
        # 1/3 = 0.333... should round to 0.33
        assert cat["pass_rate"] == pytest.approx(0.33, abs=0.01)

    def test_zero_campaigns_gives_none_rates(self):
        # Edge case: empty list per category (shouldn't happen but defensive)
        result = calculate_category_stats([])
        assert result == {}


# ── build_output tests ──────────────────────────────────────────────────────

class TestBuildOutput:
    def test_empty_categories_gives_zero_totals(self):
        output = build_output({})
        assert output["total_campaigns"] == 0
        assert output["overall_pass_rate"] is None
        assert output["categories"] == {}

    def test_total_campaigns_sums_across_categories(self):
        categories = {
            "web-scanning": {"campaigns_run": 3, "pass_rate": 1.0, "fail_rate": 0.0, "partial_rate": 0.0, "tools": ["nuclei"]},
            "secrets-detection": {"campaigns_run": 2, "pass_rate": 0.5, "fail_rate": 0.5, "partial_rate": 0.0, "tools": ["trufflehog"]},
        }
        output = build_output(categories)
        assert output["total_campaigns"] == 5

    def test_overall_pass_rate_is_weighted_average(self):
        # 3 pass in web (3 total) + 1 pass in secrets (2 total) = 4/5 = 0.80
        categories = {
            "web-scanning": {"campaigns_run": 3, "pass_rate": 1.0, "fail_rate": 0.0, "partial_rate": 0.0, "tools": ["nuclei"]},
            "secrets-detection": {"campaigns_run": 2, "pass_rate": 0.5, "fail_rate": 0.5, "partial_rate": 0.0, "tools": ["trufflehog"]},
        }
        output = build_output(categories)
        # 3*1.0 + 2*0.5 = 3 + 1 = 4 passes / 5 total
        assert output["overall_pass_rate"] == pytest.approx(0.80, abs=0.01)

    def test_output_has_required_keys(self):
        output = build_output({})
        assert "categories" in output
        assert "total_campaigns" in output
        assert "overall_pass_rate" in output
        assert "generated_at" in output
        assert "data_source" in output

    def test_output_is_json_serializable(self):
        categories = {
            "web-scanning": {"campaigns_run": 1, "pass_rate": 1.0, "fail_rate": 0.0, "partial_rate": 0.0, "tools": ["nuclei"]},
        }
        output = build_output(categories)
        # Should not raise
        json_str = json.dumps(output)
        parsed = json.loads(json_str)
        assert parsed["total_campaigns"] == 1

    def test_single_category_pass_rate_matches_overall(self):
        categories = {
            "web-scanning": {"campaigns_run": 4, "pass_rate": 0.75, "fail_rate": 0.25, "partial_rate": 0.0, "tools": ["nuclei"]},
        }
        output = build_output(categories)
        assert output["overall_pass_rate"] == pytest.approx(0.75, abs=0.01)


# ── generate_scorecard (integration) tests ─────────────────────────────────

class TestGenerateScorecard:
    def test_generates_from_real_db(self):
        rows = [
            (1, "2026-03-02", "multi_tool_campaign", "web-scanning", "pass"),
        ]
        db_path = make_db(rows)
        try:
            output = generate_scorecard(db_path)
            assert output["total_campaigns"] == 1
            assert "web-scanning" in output["categories"]
            assert output["categories"]["web-scanning"]["pass_rate"] == 1.0
        finally:
            os.unlink(db_path)

    def test_generates_from_empty_db(self):
        db_path = make_db([])
        try:
            output = generate_scorecard(db_path)
            assert output["total_campaigns"] == 0
            assert output["categories"] == {}
            assert output["overall_pass_rate"] is None
        finally:
            os.unlink(db_path)

    def test_returns_dict_not_string(self):
        db_path = make_db([])
        try:
            output = generate_scorecard(db_path)
            assert isinstance(output, dict)
        finally:
            os.unlink(db_path)

    def test_multi_category_multi_tool(self):
        rows = [
            (1, "2026-03-01", "nuclei", "web-scanning", "pass"),
            (2, "2026-03-01", "nikto", "web-scanning", "pass"),
            (3, "2026-03-01", "trufflehog", "secrets-detection", "pass"),
            (4, "2026-03-01", "trufflehog", "secrets-detection", "fail"),
            (5, "2026-03-01", "nmap", "network-recon", "partial"),
        ]
        db_path = make_db(rows)
        try:
            output = generate_scorecard(db_path)
            assert output["total_campaigns"] == 5
            assert len(output["categories"]) == 3
            assert output["categories"]["web-scanning"]["pass_rate"] == 1.0
            assert output["categories"]["secrets-detection"]["pass_rate"] == 0.5
            assert output["categories"]["network-recon"]["partial_rate"] == 1.0
        finally:
            os.unlink(db_path)

    def test_db_not_found_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            generate_scorecard("/tmp/nonexistent_campaigns_xyz.db")
