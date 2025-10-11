import streamlit as st
import requests
import numpy as np
from datetime import datetime, timedelta
import json

def get_planet_data(aoi, item_type='PSScene', asset_type='visual'):
    """
    Fetch satellite data from Planet API
    """
    try:
        # Get Planet API key from secrets
        api_key = st.secrets.get("PLANET_API_KEY")
        if not api_key:
            st.error("❌ Planet API key not found in secrets")
            return None, None

        # Create a simple geometry filter from AOI
        geometry = aoi
        
        # Define date range (last 30 days)
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Planet API request payload
        search_request = {
            "item_types": [item_type],
            "filter": {
                "type": "AndFilter",
                "config": [
                    {
                        "type": "GeometryFilter",
                        "field_name": "geometry",
                        "config": geometry
                    },
                    {
                        "type": "DateRangeFilter",
                        "field_name": "acquired",
                        "config": {
                            "gte": start_date
                        }
                    },
                    {
                        "type": "RangeFilter",
                        "field_name": "cloud_cover",
                        "config": {
                            "lte": 0.1
                        }
                    }
                ]
            }
        }

        # Search for imagery
        search_url = "https://api.planet.com/data/v1/quick-search"
        headers = {
            "Authorization": f"api-key {api_key}",
            "Content-Type": "application/json"
        }

        with st.spinner("🔍 Searching Planet imagery..."):
            response = requests.post(search_url, json=search_request, headers=headers)
            
            if response.status_code != 200:
                st.error(f"❌ Planet API error: {response.status_code} - {response.text}")
                return None, None

            results = response.json()
            items = results.get('features', [])
            
            if not items:
                st.warning("⚠️ No clear satellite images found for this area")
                return None, None

            # Get the most recent image
            latest_item = items[0]
            item_id = latest_item['id']
            properties = latest_item.get('properties', {})
            
            st.success(f"✅ Found Planet image: {item_id}")
            st.info(f"📅 Acquired: {properties.get('acquired', 'Unknown')}")
            st.info(f"☁️ Cloud cover: {properties.get('cloud_cover', 0) * 100:.1f}%")

            # For now, return mock data since actual download requires more setup
            # In production, you'd add asset activation and download here
            st.warning("🚧 Using demo data - Planet download integration in progress")
            
            # Create mock NDVI data for demonstration
            mock_ndvi = create_mock_ndvi_data(aoi)
            mock_rgb = create_mock_rgb_data(aoi)
            
            return mock_rgb, mock_ndvi

    except Exception as e:
        st.error(f"❌ Planet API error: {e}")
        return None, None

def create_mock_ndvi_data(aoi):
    """Create mock NDVI data for demonstration"""
    # Create a simple grid with some variation
    coords = aoi['coordinates'][0]
    min_lon, max_lon = min(p[0] for p in coords), max(p[0] for p in coords)
    min_lat, max_lat = min(p[1] for p in coords), max(p[1] for p in coords)
    
    # Create a synthetic NDVI image
    width, height = 200, 200
    ndvi_data = np.random.rand(height, width) * 0.8 - 0.2  # Values between -0.2 and 0.6
    
    # Add some realistic patterns - healthier vegetation in some areas
    x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
    ndvi_data += 0.3 * np.sin(3*x) * np.cos(3*y)
    ndvi_data += 0.2 * np.exp(-((x-0.7)**2 + (y-0.7)**2) / 0.1)  # Healthy spot
    
    return np.clip(ndvi_data, -1, 1)

def create_mock_rgb_data(aoi):
    """Create mock RGB data for demonstration"""
    width, height = 200, 200
    
    # Create a more realistic-looking RGB image
    rgb_data = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Base colors - mix of green (vegetation) and brown (earth)
    x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
    
    # Green vegetation areas
    green_mask = np.sin(4*x) * np.cos(4*y) > 0
    rgb_data[green_mask] = [30, 120, 30]  # Dark green
    
    # Brown earth areas
    brown_mask = ~green_mask
    rgb_data[brown_mask] = [139, 69, 19]  # Brown
    
    # Add some texture
    texture = np.random.randint(-20, 20, (height, width, 3))
    rgb_data = np.clip(rgb_data + texture, 0, 255).astype(np.uint8)
    
    return rgb_data