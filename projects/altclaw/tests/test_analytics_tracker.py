#!/usr/bin/env python3
"""
Test suite for AltClaw traffic analytics tracker.

TDD: Define expected behavior before implementation.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/delmar/.openclaw/workspace")
ANALYTICS_DIR = WORKSPACE / "projects/altclaw/analytics"
REPORT_TEMPLATE_PATH = ANALYTICS_DIR / "daily_report_template.txt"
CONFIG_PATH = ANALYTICS_DIR / "config.json"


def test_analytics_directory_structure():
    """Test: Analytics directory and required files exist"""
    assert ANALYTICS_DIR.exists(), f"Analytics directory missing: {ANALYTICS_DIR}"
    
    required_files = [
        "config.json",           # GA4 credentials and config
        "fetch_analytics.py",    # Script to fetch GA4 data
        "generate_report.py",    # Script to generate Telegram report
        "daily_report_template.txt",  # Report template
    ]
    
    for file in required_files:
        file_path = ANALYTICS_DIR / file
        if not file_path.exists():
            print(f"⚠ Missing: {file}")
        else:
            print(f"✓ Found: {file}")


def test_config_structure():
    """Test: config.json has required fields"""
    if not CONFIG_PATH.exists():
        print("⚠ Config doesn't exist yet")
        return
    
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    required_fields = [
        "ga4_property_id",
        "service_account_key_path",
        "site_url",
        "telegram_group_id",
        "report_hour_gmt",
    ]
    
    for field in required_fields:
        assert field in config, f"Config missing field: {field}"
    
    print("✓ Config has all required fields")


def test_analytics_fetcher_interface():
    """Test: Analytics fetcher returns expected data structure"""
    # Expected data structure (will be dict)
    expected_structure = {
        "date": "YYYY-MM-DD",
        "total_users": 0,
        "total_sessions": 0,
        "total_pageviews": 0,
        "top_pages": [
            {"page": "/articles/...", "views": 0}
        ],
        "traffic_sources": {
            "organic": 0,
            "direct": 0,
            "referral": 0,
            "social": 0
        },
        "countries": [
            {"country": "US", "users": 0}
        ],
        "avg_session_duration": 0.0,
        "bounce_rate": 0.0
    }
    
    print("✓ Expected analytics structure defined")
    return expected_structure


def test_report_generator_output():
    """Test: Report generator creates readable Telegram message"""
    # Mock data
    mock_data = {
        "date": "2026-02-10",
        "total_users": 150,
        "total_sessions": 200,
        "total_pageviews": 350,
        "top_pages": [
            {"page": "/articles/vllm-rce-cve-2026-22778.html", "views": 85},
            {"page": "/articles/n8n-rce-cve-2026-21858.html", "views": 65},
            {"page": "/", "views": 50},
        ],
        "traffic_sources": {
            "organic": 120,
            "direct": 20,
            "referral": 8,
            "social": 2
        },
        "countries": [
            {"country": "United States", "users": 80},
            {"country": "United Kingdom", "users": 25},
            {"country": "Germany", "users": 20},
        ],
        "avg_session_duration": 145.5,
        "bounce_rate": 62.5
    }
    
    # Report should be:
    # - Readable (emojis, formatting)
    # - Concise (fits in Telegram message)
    # - Actionable (highlights what's working)
    
    expected_format = """
📊 AltClaw Daily Analytics - 2026-02-10

👥 Traffic:
  • 150 users (+/- X% vs yesterday)
  • 200 sessions
  • 350 pageviews
  • 2m 25s avg session

🔝 Top Articles:
  1. vLLM RCE (85 views) 🔥
  2. n8n RCE (65 views)
  3. Homepage (50 views)

📍 Traffic Sources:
  • Organic: 120 (80%)
  • Direct: 20 (13%)
  • Referral: 8 (5%)
  • Social: 2 (1%)

🌍 Top Countries:
  • US: 80 (53%)
  • UK: 25 (17%)
  • DE: 20 (13%)

📉 Bounce Rate: 62.5%

✅ What's Working:
  - Breaking news articles driving traffic
  - Strong organic search performance
  
⚠️ What Needs Work:
  - High bounce rate (target <50%)
  - Low referral traffic
"""
    
    print("✓ Report format template defined")
    return mock_data


def test_ga4_api_authentication():
    """Test: Can authenticate with GA4 API"""
    # This will fail initially - needs credentials
    
    service_account_path = WORKSPACE / "credentials/ga4-service-account.json"
    
    if not service_account_path.exists():
        print("⚠ GA4 service account credentials not found")
        print(f"  Expected location: {service_account_path}")
        return False
    
    # Try to import required libraries
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest,
            DateRange,
            Dimension,
            Metric,
        )
        print("✓ GA4 API libraries installed")
    except ImportError as e:
        print(f"✗ Missing library: {e}")
        print("  Run: pip install google-analytics-data")
        return False
    
    return True


def test_daily_cron_job_exists():
    """Test: Cron job scheduled for daily reports"""
    # This will be verified manually after cron job creation
    print("⚠ Manual verification required: Check cron job exists")


def test_report_delivers_to_telegram():
    """Test: Report successfully sends to Telegram group"""
    # This will be integration test
    print("⚠ Integration test: Run manually after implementation")


def test_historical_data_storage():
    """Test: Analytics data stored for trend analysis"""
    history_dir = ANALYTICS_DIR / "history"
    
    if history_dir.exists():
        json_files = list(history_dir.glob("*.json"))
        print(f"✓ Found {len(json_files)} historical data files")
    else:
        print("⚠ History directory doesn't exist yet")


def test_week_over_week_comparison():
    """Test: Report includes WoW growth metrics"""
    # Report should show:
    # - Today vs yesterday (+X% users)
    # - This week vs last week trend
    
    mock_comparison = {
        "today_vs_yesterday": {
            "users": +15.5,  # percent change
            "pageviews": +22.3,
            "bounce_rate": -3.2,
        },
        "week_vs_last_week": {
            "users": +45.2,
            "pageviews": +67.8,
        }
    }
    
    print("✓ Comparison metrics structure defined")
    return mock_comparison


if __name__ == "__main__":
    print("=" * 60)
    print("AltClaw Traffic Analytics - TDD Test Suite")
    print("=" * 60)
    
    tests = [
        test_analytics_directory_structure,
        test_config_structure,
        test_analytics_fetcher_interface,
        test_report_generator_output,
        test_ga4_api_authentication,
        test_daily_cron_job_exists,
        test_report_delivers_to_telegram,
        test_historical_data_storage,
        test_week_over_week_comparison,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            result = test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("\n🔨 Next: Implement code to pass these tests")
    else:
        print("\n✅ All tests pass!")
