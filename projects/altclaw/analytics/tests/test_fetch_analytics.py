#!/usr/bin/env python3
"""Unit tests for fetch_analytics.py - syntax and structure validation"""

from pathlib import Path
import json

def test_script_exists_and_executable():
    """Test: Script exists and is executable"""
    script = Path(__file__).parent.parent / "fetch_analytics.py"
    assert script.exists(), "fetch_analytics.py not found"
    assert script.stat().st_mode & 0o111, "Script not executable"
    print("✓ Script exists and is executable")

def test_uses_venv_python():
    """Test: Script uses venv Python"""
    script = Path(__file__).parent.parent / "fetch_analytics.py"
    with open(script) as f:
        shebang = f.readline()
    assert "venv/bin/python" in shebang, "Script must use venv Python"
    print("✓ Uses venv Python interpreter")

def test_config_valid():
    """Test: Config file is valid JSON with required fields"""
    config_path = Path(__file__).parent.parent / "config.json"
    assert config_path.exists(), "config.json not found"
    
    with open(config_path) as f:
        config = json.load(f)
    
    required = ["ga4_property_id", "service_account_key_path"]
    for field in required:
        assert field in config, f"Config missing: {field}"
    
    print("✓ Config is valid")

def test_history_directory_exists():
    """Test: History directory exists for data storage"""
    history_dir = Path(__file__).parent.parent / "history"
    assert history_dir.exists(), "history/ directory not found"
    assert history_dir.is_dir()
    print("✓ History directory exists")

def test_requirements_file_exists():
    """Test: requirements.txt exists"""
    req_file = Path(__file__).parent.parent / "requirements.txt"
    assert req_file.exists(), "requirements.txt not found"
    
    with open(req_file) as f:
        content = f.read()
    assert "google-analytics-data" in content
    
    print("✓ Requirements file exists")

if __name__ == "__main__":
    print("=" * 50)
    print("fetch_analytics.py Unit Tests")
    print("=" * 50)
    
    tests = [
        test_script_exists_and_executable,
        test_uses_venv_python,
        test_config_valid,
        test_history_directory_exists,
        test_requirements_file_exists,
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
