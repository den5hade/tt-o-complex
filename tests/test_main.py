import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from pathlib import Path

client = TestClient(app)

def test_home_page():
    """Test the home page loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Weather Forecast" in response.text

def test_weather_endpoint_english():
    """Test weather endpoint with English city name."""
    response = client.get("/api/weather/London")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "forecast" in data
    assert data["city"] == "London"

def test_weather_endpoint_russian():
    """Test weather endpoint with Russian city name."""
    response = client.get("/api/weather/Москва")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "forecast" in data
    assert data["city"] == "Москва"

def test_weather_endpoint_invalid_city():
    """Test weather endpoint with invalid city name."""
    response = client.get("/api/weather/NonExistentCity123")
    assert response.status_code == 500

def test_suggestions_endpoint_english():
    """Test suggestions endpoint with English query."""
    response = client.get("/api/suggestions/Lon")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_suggestions_endpoint_russian():
    """Test suggestions endpoint with Russian query."""
    response = client.get("/api/suggestions/Мос")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_csv_files_exist():
    """Test that required CSV files exist."""
    world_cities_path = Path("app/csv/worldcities.csv")
    russian_cities_path = Path("app/csv/russiacities.csv")
    
    assert world_cities_path.exists(), "worldcities.csv not found"
    assert russian_cities_path.exists(), "russiacities.csv not found" 