#!/usr/bin/env python3
"""
Tests for product-discovery.py

Tests the product discovery automation that scans research files
for product mentions and generates discovery reports.
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from product_discovery import (
    load_discovery_log,
    save_discovery_log,
    get_validated_products,
    scan_research_files,
    generate_discovery_report
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace structure"""
    # Create directory structure
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    
    validated_products = tmp_path / "VALIDATED_PRODUCTS.md"
    discovery_log = tmp_path / "discovery-log.json"
    
    # Create sample validated products file
    validated_products.write_text("""
# Validated Products

## Books

### Test Book 1
- **ASIN:** 1234567890
- **Price:** $50

### Test Book 2
- **ASIN:** B00TEST001
- **Price:** $40
""")
    
    return {
        "workspace": tmp_path,
        "research_dir": research_dir,
        "validated_products": validated_products,
        "discovery_log": discovery_log
    }


@pytest.fixture
def sample_research_files(temp_workspace):
    """Create sample research files with product mentions"""
    research_dir = temp_workspace["research_dir"]
    
    # Recent file with product mentions
    recent_file = research_dir / "2026-02-10-daily-research.md"
    recent_file.write_text("""
# Daily Research

Found interesting tool: Burp Suite Professional for API testing.
Also discovered new WiFi adapter: Alfa AWUS036ACHM.
Book recommendation: The Hacker Playbook 3
""")
    
    # Old file (shouldn't be scanned)
    old_file = research_dir / "2020-01-01-old-research.md"
    old_file.write_text("Old content with Metasploit mention")
    
    return temp_workspace


class TestDiscoveryLog:
    """Test discovery log loading and saving"""
    
    def test_load_empty_log(self, temp_workspace):
        """Test loading when log doesn't exist"""
        log = load_discovery_log()
        assert "discovered" in log
        assert "rejected" in log
        assert log["discovered"] == []
        assert log["rejected"] == []
    
    def test_save_and_load_log(self, temp_workspace, monkeypatch):
        """Test saving and loading discovery log"""
        log_path = temp_workspace["discovery_log"]
        
        # Mock the DISCOVERY_LOG path
        import product_discovery
        monkeypatch.setattr(product_discovery, "DISCOVERY_LOG", log_path)
        
        test_log = {
            "discovered": [
                {"product": "Test Product", "source_file": "test.md", "date": "2026-02-10"}
            ],
            "rejected": []
        }
        
        save_discovery_log(test_log)
        assert log_path.exists()
        
        loaded = load_discovery_log()
        assert loaded["discovered"] == test_log["discovered"]


class TestValidatedProducts:
    """Test validated products extraction"""
    
    def test_extract_asins(self, temp_workspace, monkeypatch):
        """Test extracting ASINs from VALIDATED_PRODUCTS.md"""
        import product_discovery
        monkeypatch.setattr(product_discovery, "VALIDATED_PRODUCTS", temp_workspace["validated_products"])
        
        asins = get_validated_products()
        assert "1234567890" in asins
        assert "B00TEST001" in asins
        assert len(asins) == 2
    
    def test_no_products_file(self, tmp_path, monkeypatch):
        """Test when VALIDATED_PRODUCTS.md doesn't exist"""
        import product_discovery
        monkeypatch.setattr(product_discovery, "VALIDATED_PRODUCTS", tmp_path / "nonexistent.md")
        
        asins = get_validated_products()
        assert len(asins) == 0


class TestResearchScanning:
    """Test research file scanning"""
    
    def test_scan_finds_products(self, sample_research_files, monkeypatch):
        """Test scanning research files finds product mentions"""
        import product_discovery
        monkeypatch.setattr(product_discovery, "RESEARCH_DIR", sample_research_files["research_dir"])
        
        findings = scan_research_files(days=7)
        
        # Should find Burp Suite, WiFi adapter, book
        assert len(findings) > 0
        product_names = [f["product"].lower() for f in findings]
        assert any("burp" in p for p in product_names)
    
    def test_scan_respects_date_limit(self, sample_research_files, monkeypatch):
        """Test scanning only includes recent files"""
        import product_discovery
        import os
        import time
        
        monkeypatch.setattr(product_discovery, "RESEARCH_DIR", sample_research_files["research_dir"])
        
        # Set old file to actually be old (modify its mtime)
        old_file = sample_research_files["research_dir"] / "2020-01-01-old-research.md"
        old_timestamp = time.mktime(time.strptime("2020-01-01", "%Y-%m-%d"))
        os.utime(old_file, (old_timestamp, old_timestamp))
        
        # Scan last 1 day - should only get recent file
        findings = scan_research_files(days=1)
        
        # Old file from 2020 should not be included
        source_files = [f["source_file"] for f in findings]
        assert not any("2020" in sf for sf in source_files)
    
    def test_scan_empty_directory(self, temp_workspace, monkeypatch):
        """Test scanning when no research files exist"""
        import product_discovery
        monkeypatch.setattr(product_discovery, "RESEARCH_DIR", temp_workspace["research_dir"])
        
        findings = scan_research_files(days=7)
        assert findings == []


class TestReportGeneration:
    """Test discovery report generation"""
    
    def test_generate_report_with_findings(self):
        """Test generating report with product findings"""
        findings = [
            {"product": "Burp Suite", "source_file": "research.md", "date": "2026-02-10"},
            {"product": "WiFi Adapter", "source_file": "research.md", "date": "2026-02-10"}
        ]
        validated_asins = {"1234567890", "B00TEST001"}
        
        report = generate_discovery_report(findings, validated_asins)
        
        assert "Product Discovery Report" in report
        assert "Burp Suite" in report
        assert "WiFi Adapter" in report
        assert "2 products mentioned" in report
    
    def test_generate_report_no_findings(self):
        """Test generating report with no findings"""
        findings = []
        validated_asins = set()
        
        report = generate_discovery_report(findings, validated_asins)
        
        assert "Product Discovery Report" in report
        assert "No new product candidates" in report
    
    def test_report_deduplicates(self):
        """Test report deduplicates product mentions"""
        findings = [
            {"product": "Burp Suite", "source_file": "research1.md", "date": "2026-02-10"},
            {"product": "burp suite", "source_file": "research2.md", "date": "2026-02-11"},  # Duplicate
        ]
        validated_asins = set()
        
        report = generate_discovery_report(findings, validated_asins)
        
        # Should only show once (case-insensitive dedup)
        burp_count = report.lower().count("### burp suite")
        assert burp_count == 1


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_discovery_workflow(self, sample_research_files, monkeypatch):
        """Test complete discovery workflow"""
        import product_discovery
        
        # Mock paths
        monkeypatch.setattr(product_discovery, "RESEARCH_DIR", sample_research_files["research_dir"])
        monkeypatch.setattr(product_discovery, "VALIDATED_PRODUCTS", sample_research_files["validated_products"])
        monkeypatch.setattr(product_discovery, "DISCOVERY_LOG", sample_research_files["discovery_log"])
        
        # Run discovery
        findings = scan_research_files(days=7)
        validated_asins = get_validated_products()
        report = generate_discovery_report(findings, validated_asins)
        
        # Verify results
        assert len(findings) > 0
        assert len(validated_asins) == 2
        assert "Product Discovery Report" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
