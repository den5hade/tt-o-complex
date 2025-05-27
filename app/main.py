from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
from typing import List, Dict, Optional
import json
from pathlib import Path
import pandas as pd
import re

app = FastAPI(title="Weather Forecast App")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Open-Meteo API base URL
WEATHER_API_BASE = "https://api.open-meteo.com/v1"

def is_cyrillic(text: str) -> bool:
    """Check if the text contains Cyrillic characters."""
    result = bool(re.search('[\u0400-\u04FF]', text))
    print(f"Checking if '{text}' is Cyrillic: {result}")
    return result

def load_cities_data():
    """Load both world cities and Russian cities data."""
    try:
        world_cities = pd.read_csv('app/csv/worldcities.csv')
        russian_cities = pd.read_csv('app/csv/russiacities.csv')
        print(f"Loaded {len(russian_cities)} Russian cities")
        print("Sample of Russian cities:", russian_cities['city'].head().tolist())
        return world_cities, russian_cities
    except FileNotFoundError as e:
        raise Exception(f"CSV file not found: {str(e)}")

# Initialize cities data
world_cities_df, russian_cities_df = load_cities_data()

def find_city_coordinates(city_name: str) -> Optional[Dict]:
    """Find city coordinates from the appropriate CSV file based on input language."""
    print(f"Searching for city: {city_name}")
    print(f"Is Cyrillic: {is_cyrillic(city_name)}")
    
    # Convert to lowercase for case-insensitive comparison
    city_name = city_name.lower()
    
    # Choose the appropriate dataframe based on input language
    if is_cyrillic(city_name):
        df = russian_cities_df
        print("Using Russian cities database")
        print("Available cities:", df['city'].tolist()[:5])  # Print first 5 cities
    else:
        df = world_cities_df
        print("Using world cities database")
    
    df['city_lower'] = df['city'].str.lower()
    
    # Find exact match first
    exact_match = df[df['city_lower'] == city_name]
    print(f"Exact matches found: {len(exact_match)}")
    
    if not exact_match.empty:
        city_data = exact_match.iloc[0]
        return {
            "name": city_data['city'],
            "latitude": city_data['lat'],
            "longitude": city_data['lng']
        }
    
    # If no exact match, find partial matches
    partial_matches = df[df['city_lower'].str.contains(city_name, na=False)]
    print(f"Partial matches found: {len(partial_matches)}")
    if not partial_matches.empty:
        print("Partial matches:", partial_matches['city'].tolist()[:5])
        city_data = partial_matches.iloc[0]
        return {
            "name": city_data['city'],
            "latitude": city_data['lat'],
            "longitude": city_data['lng']
        }
    
    return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with the weather search form."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/api/weather/{city}")
async def get_weather(city: str):
    """Get weather forecast for a specific city."""
    try:
        # Get coordinates from local CSV file
        location = find_city_coordinates(city)
        if not location:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Get weather forecast
        async with httpx.AsyncClient() as client:
            weather_response = await client.get(
                f"{WEATHER_API_BASE}/forecast",
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "hourly": "temperature_2m,precipitation_probability,weathercode",
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": "auto"
                }
            )
            
            return {
                "city": location["name"],
                "location": location,
                "forecast": weather_response.json()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 