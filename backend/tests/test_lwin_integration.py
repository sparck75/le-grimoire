"""
Tests for LWIN Integration

Tests for Wine model LWIN fields, LWINService, and LWIN API endpoints.
"""
import pytest
from app.models.mongodb.wine import Wine
from app.services.lwin_service import LWINService
from datetime import datetime


class TestWineModelLWIN:
    """Test Wine model LWIN fields and validators"""
    
    def test_lwin7_validation_valid(self):
        """Test valid LWIN7 code"""
        wine = Wine(
            name="Test Wine",
            lwin7="1234567"
        )
        assert wine.lwin7 == "1234567"
    
    def test_lwin7_validation_invalid_length(self):
        """Test LWIN7 with invalid length"""
        with pytest.raises(ValueError, match="LWIN7 must be exactly 7 digits"):
            Wine(
                name="Test Wine",
                lwin7="123456"  # Only 6 digits
            )
    
    def test_lwin7_validation_invalid_chars(self):
        """Test LWIN7 with non-digit characters"""
        with pytest.raises(ValueError, match="LWIN7 must be exactly 7 digits"):
            Wine(
                name="Test Wine",
                lwin7="12345AB"  # Contains letters
            )
    
    def test_lwin11_validation_valid(self):
        """Test valid LWIN11 code"""
        wine = Wine(
            name="Test Wine",
            lwin11="12345672015"
        )
        assert wine.lwin11 == "12345672015"
    
    def test_lwin11_validation_invalid(self):
        """Test LWIN11 with invalid length"""
        with pytest.raises(ValueError, match="LWIN11 must be exactly 11 digits"):
            Wine(
                name="Test Wine",
                lwin11="1234567201"  # Only 10 digits
            )
    
    def test_lwin18_validation_valid(self):
        """Test valid LWIN18 code"""
        wine = Wine(
            name="Test Wine",
            lwin18="123456720151200750"
        )
        assert wine.lwin18 == "123456720151200750"
    
    def test_lwin18_validation_invalid(self):
        """Test LWIN18 with invalid length"""
        with pytest.raises(ValueError, match="LWIN18 must be exactly 18 digits"):
            Wine(
                name="Test Wine",
                lwin18="12345672015120075"  # Only 17 digits
            )
    
    def test_all_lwin_codes(self):
        """Test wine with all LWIN codes"""
        wine = Wine(
            name="Château Margaux 2015",
            lwin7="1234567",
            lwin11="12345672015",
            lwin18="123456720151200750",
            producer="Château Margaux",
            vintage=2015,
            data_source="lwin"
        )
        assert wine.lwin7 == "1234567"
        assert wine.lwin11 == "12345672015"
        assert wine.lwin18 == "123456720151200750"
        assert wine.data_source == "lwin"


class TestLWINService:
    """Test LWINService functionality"""
    
    def test_normalize_wine_type_red(self):
        """Test wine type normalization for red wines"""
        service = LWINService()
        assert service._normalize_wine_type("red") == "red"
        assert service._normalize_wine_type("Red") == "red"
        assert service._normalize_wine_type("RED") == "red"
        assert service._normalize_wine_type("rouge") == "red"
    
    def test_normalize_wine_type_white(self):
        """Test wine type normalization for white wines"""
        service = LWINService()
        assert service._normalize_wine_type("white") == "white"
        assert service._normalize_wine_type("White") == "white"
        assert service._normalize_wine_type("blanc") == "white"
    
    def test_normalize_wine_type_sparkling(self):
        """Test wine type normalization for sparkling wines"""
        service = LWINService()
        assert service._normalize_wine_type("sparkling") == "sparkling"
        assert service._normalize_wine_type("Champagne") == "sparkling"
        assert service._normalize_wine_type("pétillant") == "sparkling"
    
    def test_normalize_wine_type_default(self):
        """Test wine type normalization default value"""
        service = LWINService()
        assert service._normalize_wine_type(None) == "red"
        assert service._normalize_wine_type("unknown") == "red"
    
    def test_get_field(self):
        """Test field retrieval from CSV row"""
        service = LWINService()
        row = {
            "Name": "Château Margaux",
            "Producer": "Château Margaux",
            "Country": "France"
        }
        
        # Test exact match
        assert service._get_field(row, ["Name"]) == "Château Margaux"
        
        # Test with aliases
        assert service._get_field(row, ["name", "Name", "wine_name"]) == "Château Margaux"
        
        # Test non-existent field
        assert service._get_field(row, ["missing"]) is None
    
    def test_transform_lwin_row_minimal(self):
        """Test CSV row transformation with minimal data"""
        service = LWINService()
        row = {
            "lwin7": "1234567",
            "name": "Test Wine"
        }
        
        result = service._transform_lwin_row(row)
        
        assert result is not None
        assert result["lwin7"] == "1234567"
        assert result["name"] == "Test Wine"
        assert result["data_source"] == "lwin"
        assert result["user_id"] is None
    
    def test_transform_lwin_row_complete(self):
        """Test CSV row transformation with complete data"""
        service = LWINService()
        row = {
            "lwin7": "1234567",
            "lwin11": "12345672015",
            "name": "Château Margaux",
            "producer": "Château Margaux",
            "vintage": "2015",
            "country": "France",
            "region": "Bordeaux",
            "appellation": "Margaux",
            "type": "Red",
            "grapes": "Cabernet Sauvignon, Merlot",
            "alcohol": "13.5",
            "classification": "First Growth"
        }
        
        result = service._transform_lwin_row(row)
        
        assert result is not None
        assert result["lwin7"] == "1234567"
        assert result["lwin11"] == "12345672015"
        assert result["name"] == "Château Margaux"
        assert result["producer"] == "Château Margaux"
        assert result["vintage"] == 2015
        assert result["country"] == "France"
        assert result["region"] == "Bordeaux"
        assert result["appellation"] == "Margaux"
        assert result["wine_type"] == "red"
        assert result["alcohol_content"] == 13.5
        assert result["classification"] == "First Growth"
        assert len(result["grape_varieties"]) == 2
        assert result["grape_varieties"][0]["name"] == "Cabernet Sauvignon"
        assert result["grape_varieties"][1]["name"] == "Merlot"
    
    def test_transform_lwin_row_invalid(self):
        """Test CSV row transformation with invalid data"""
        service = LWINService()
        
        # Row with no name and no LWIN
        row = {
            "producer": "Some Producer"
        }
        
        result = service._transform_lwin_row(row)
        assert result is None
    
    def test_transform_lwin_row_name_generation(self):
        """Test automatic name generation from producer and vintage"""
        service = LWINService()
        row = {
            "lwin7": "1234567",
            "producer": "Château Test",
            "vintage": "2020"
        }
        
        result = service._transform_lwin_row(row)
        
        assert result is not None
        assert result["name"] == "Château Test 2020"


class TestLWINCSVParsing:
    """Test CSV parsing functionality"""
    
    def test_parse_csv_format_variations(self):
        """Test parsing CSV with different column name formats"""
        service = LWINService()
        
        # This would require creating actual CSV files
        # Skipping for now as it requires file I/O
        pass


class TestLWINAPIEndpoints:
    """Test LWIN API endpoints"""
    
    # These tests would use FastAPI TestClient
    # and require async test setup with database
    # Skipping for now as they require full environment
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
