"""
generate_scorecard.py — SecurityClaw → bughuntertools.com Scorecard Data Generator

Reads campaigns.db and outputs a JSON file for the bughuntertools.com 11ty site.

Usage:
    python3 generate_scorecard.py [--db /path/to/campaigns.db] [--out /path/to/output.json]

Output: securityclaw_scorecard.json consumed by 11ty at build time.
"""
import argparse
import json
import os
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


DB_DEFAULT = "/home/delmar/.openclaw/agents/peng/workspace/projects/security/campaign-manager/campaigns.db"
OUT_DEFAULT = (
    "/home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/"
    "bughuntertools.com/src/_data/securityclaw_scorecard.json"
)


def calculate_category_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Given a list of row dicts {category, result, tool}, return per-category stats.

    Returns:
        {
            "web-scanning": {
                "campaigns_run": 4,
                "pass_rate": 0.75,
                "fail_rate": 0.25,
                "partial_rate": 0.0,
                "tools": ["nuclei", "nikto"]
            },
            ...
        }
    """
    if not rows:
        return {}

    # Aggregate
    agg: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"campaigns_run": 0, "pass": 0, "partial": 0, "fail": 0, "tools": set()}
    )

    for row in rows:
        cat = row["category"]
        result = row["result"]
        tool = row["tool"]
        agg[cat]["campaigns_run"] += 1
        if result in ("pass", "partial", "fail"):
            agg[cat][result] += 1
        agg[cat]["tools"].add(tool)

    # Build output
    stats: Dict[str, Any] = {}
    for cat, data in agg.items():
        total = data["campaigns_run"]
        stats[cat] = {
            "campaigns_run": total,
            "pass_rate": round(data["pass"] / total, 2) if total > 0 else None,
            "partial_rate": round(data["partial"] / total, 2) if total > 0 else None,
            "fail_rate": round(data["fail"] / total, 2) if total > 0 else None,
            "tools": sorted(data["tools"]),
        }

    return stats


def build_output(categories: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the final output dict from per-category stats.

    Args:
        categories: Result of calculate_category_stats()

    Returns:
        Complete scorecard dict ready for JSON serialisation.
    """
    total_campaigns = sum(c["campaigns_run"] for c in categories.values())

    # Weighted overall pass rate
    if total_campaigns > 0:
        total_passes = sum(
            round(c["pass_rate"] * c["campaigns_run"])
            for c in categories.values()
            if c.get("pass_rate") is not None
        )
        overall_pass_rate = round(total_passes / total_campaigns, 2)
    else:
        overall_pass_rate = None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "campaigns.db / SecurityClaw campaign_results table",
        "total_campaigns": total_campaigns,
        "overall_pass_rate": overall_pass_rate,
        "categories": categories,
    }


def generate_scorecard(db_path: str) -> Dict[str, Any]:
    """
    Read campaigns.db and return scorecard data dict.

    Args:
        db_path: Path to campaigns.db

    Returns:
        Scorecard dict

    Raises:
        FileNotFoundError: if db_path does not exist
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"campaigns.db not found at: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT tool, category, result FROM campaign_results ORDER BY recorded_at ASC")
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    category_stats = calculate_category_stats(rows)
    return build_output(category_stats)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SecurityClaw scorecard JSON for bughuntertools.com"
    )
    parser.add_argument("--db", default=DB_DEFAULT, help="Path to campaigns.db")
    parser.add_argument("--out", default=OUT_DEFAULT, help="Path to output JSON file")
    args = parser.parse_args()

    print(f"Reading: {args.db}")
    data = generate_scorecard(args.db)
    print(f"  total_campaigns: {data['total_campaigns']}")
    print(f"  categories: {list(data['categories'].keys())}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Written: {args.out}")


if __name__ == "__main__":
    main()
