#!/usr/bin/env python3
"""
Tests for product-verification.py

Tests the monthly product verification that checks ASIN availability
and generates verification reports for manual price updates.
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from product_verification import (
    extract_products,
    generate_verification_report
)


@pytest.fixture
def temp_validated_products(tmp_path):
    """Create temporary VALIDATED_PRODUCTS.md"""
    products_file = tmp_path / "VALIDATED_PRODUCTS.md"
    products_file.write_text("""
# Validated Products

## Books

### Test Book 1
- **ASIN:** 1234567890
- **Price:** $50
- **Commission:** 4.5% (~$2.25)

### Test Book 2
- **ASIN:** B00TEST001
- **Price:** $40
- **Commission:** 4.5% (~$1.80)

## Hardware

### WiFi Adapter
- **ASIN:** B07WIFI123
- **Price:** $35-45
- **Commission:** 3% (~$1.20)
""")
    return products_file


class TestProductExtraction:
    """Test extracting products from VALIDATED_PRODUCTS.md"""
    
    def test_extract_products(self, temp_validated_products, monkeypatch):
        """Test extracting all products with ASINs"""
        import product_verification
        monkeypatch.setattr(product_verification, "VALIDATED_PRODUCTS", temp_validated_products)
        
        products = extract_products()
        
        assert len(products) == 3
        asins = [p["asin"] for p in products]
        assert "1234567890" in asins
        assert "B00TEST001" in asins
        assert "B07WIFI123" in asins
    
    def test_extract_products_with_names(self, temp_validated_products, monkeypatch):
        """Test product names are extracted correctly"""
        import product_verification
        monkeypatch.setattr(product_verification, "VALIDATED_PRODUCTS", temp_validated_products)
        
        products = extract_products()
        
        names = [p["name"] for p in products]
        assert "Test Book 1" in names
        assert "Test Book 2" in names
        assert "WiFi Adapter" in names
    
    def test_extract_products_with_prices(self, temp_validated_products, monkeypatch):
        """Test prices are extracted"""
        import product_verification
        monkeypatch.setattr(product_verification, "VALIDATED_PRODUCTS", temp_validated_products)
        
        products = extract_products()
        
        # Check prices are extracted (as strings)
        prices = [p["price"] for p in products]
        assert any("50" in p for p in prices)
        assert any("40" in p for p in prices)
    
    def test_extract_no_file(self, tmp_path, monkeypatch):
        """Test when VALIDATED_PRODUCTS.md doesn't exist"""
        import product_verification
        monkeypatch.setattr(product_verification, "VALIDATED_PRODUCTS", tmp_path / "nonexistent.md")
        
        products = extract_products()
        assert products == []


class TestReportGeneration:
    """Test verification report generation"""
    
    def test_generate_report_all_available(self):
        """Test report when all products are available"""
        products = [
            {"name": "Test Product 1", "asin": "1234567890", "price": "50"},
            {"name": "Test Product 2", "asin": "B00TEST001", "price": "40"}
        ]
        results = [
            {"available": True, "current_price": None, "verified_date": "2026-02-11"},
            {"available": True, "current_price": None, "verified_date": "2026-02-11"}
        ]
        
        report = generate_verification_report(products, results)
        
        assert "Product Verification Report" in report
        assert "2 products" in report or "Products Checked: 2" in report
        assert "100.0%" in report  # 100% availability
        assert "Available:** 2 products" in report
    
    def test_generate_report_some_unavailable(self):
        """Test report when some products are unavailable"""
        products = [
            {"name": "Available Product", "asin": "1234567890", "price": "50"},
            {"name": "Unavailable Product", "asin": "B00GONE123", "price": "40"}
        ]
        results = [
            {"available": True, "current_price": None, "verified_date": "2026-02-11"},
            {"available": False, "current_price": None, "verified_date": "2026-02-11"}
        ]
        
        report = generate_verification_report(products, results)
        
        assert "Unavailable:** 1 products" in report
        assert "50.0%" in report  # 50% availability
        assert "Unavailable Product" in report
    
    def test_generate_report_with_price_changes(self):
        """Test report shows price changes"""
        products = [
            {"name": "Test Product", "asin": "1234567890", "price": "50"}
        ]
        results = [
            {"available": True, "current_price": "65", "verified_date": "2026-02-11"}
        ]
        
        report = generate_verification_report(products, results)
        
        # Should show price change > 20%
        assert "Price Change" in report or "Current Price" in report
    
    def test_report_includes_actions(self):
        """Test report includes action items"""
        products = [
            {"name": "Test Product", "asin": "1234567890", "price": "50"}
        ]
        results = [
            {"available": False, "current_price": None, "verified_date": "2026-02-11"}
        ]
        
        report = generate_verification_report(products, results)
        
        assert "Actions Required" in report
        assert "Unavailable Products" in report


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_verification_workflow(self, temp_validated_products, monkeypatch):
        """Test complete verification workflow"""
        import product_verification
        
        monkeypatch.setattr(product_verification, "VALIDATED_PRODUCTS", temp_validated_products)
        
        # Extract products
        products = extract_products()
        assert len(products) > 0
        
        # Simulate verification results (all available)
        results = [
            {"available": True, "current_price": None, "verified_date": "2026-02-11"}
            for _ in products
        ]
        
        # Generate report
        report = generate_verification_report(products, results)
        
        assert "Product Verification Report" in report
        assert "100.0%" in report  # All available


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
