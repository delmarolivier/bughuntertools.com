#!/usr/bin/env python3
"""Unit tests for generate_report.py - syntax and structure validation"""

from pathlib import Path
import json

def test_script_exists_and_executable():
    """Test: Script exists and is executable"""
    script = Path(__file__).parent.parent / "generate_report.py"
    assert script.exists(), "generate_report.py not found"
    assert script.stat().st_mode & 0o111, "Script not executable"
    print("✓ Script exists and is executable")

def test_uses_venv_python():
    """Test: Script uses venv Python"""
    script = Path(__file__).parent.parent / "generate_report.py"
    with open(script) as f:
        shebang = f.readline()
    assert "venv/bin/python" in shebang, "Script must use venv Python"
    print("✓ Uses venv Python interpreter")

def test_report_template_exists():
    """Test: Report template file exists"""
    template = Path(__file__).parent.parent / "daily_report_template.txt"
    assert template.exists(), "daily_report_template.txt not found"
    
    with open(template) as f:
        content = f.read()
    
    # Verify template has key sections
    assert "📊 AltClaw Daily Analytics" in content
    assert "👥 Traffic:" in content
    assert "🔝 Top Articles:" in content
    
    print("✓ Report template exists")

def test_mock_data_format():
    """Test: Can create and read mock analytics data"""
    history_dir = Path(__file__).parent.parent / "history"
    history_dir.mkdir(exist_ok=True)
    
    mock_file = history_dir / "test-mock.json"
    
    mock_data = {
        "date": "2026-02-10",
        "total_users": 100,
        "total_sessions": 150,
        "total_pageviews": 250,
        "avg_session_duration": 120.0,
        "bounce_rate": 55.5,
        "top_pages": [{"page": "/test", "views": 50}],
        "traffic_sources": {"organic": 80, "direct": 20},
        "countries": [{"country": "Test", "users": 100}]
    }
    
    with open(mock_file, "w") as f:
        json.dump(mock_data, f)
    
    # Verify can read back
    with open(mock_file) as f:
        loaded = json.load(f)
    
    assert loaded["total_users"] == 100
    
    # Cleanup
    mock_file.unlink()
    
    print("✓ Mock data format validated")

def test_script_has_main_function():
    """Test: Script has main() function"""
    script = Path(__file__).parent.parent / "generate_report.py"
    with open(script) as f:
        content = f.read()
    
    assert "def main():" in content
    assert "if __name__ == \"__main__\":" in content
    
    print("✓ Script has main() function")

if __name__ == "__main__":
    print("=" * 50)
    print("generate_report.py Unit Tests")
    print("=" * 50)
    
    tests = [
        test_script_exists_and_executable,
        test_uses_venv_python,
        test_report_template_exists,
        test_mock_data_format,
        test_script_has_main_function,
    ]
    
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {test.__name__}: {e}")
            exit(1)
    
    print(f"\n✅ All {passed} tests passed")
