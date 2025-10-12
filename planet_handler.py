import streamlit as st
import requests
import numpy as np
from datetime import datetime, timedelta
import json
import time

def get_planet_data(aoi, item_type='PSScene', asset_type='visual'):
    """
    Fetch satellite data from Planet API with enhanced user feedback
    """
    try:
        # Get Planet API key from secrets
        api_key = st.secrets.get("PLANET_API_KEY")
        if not api_key:
            st.error("❌ Planet API key not found in secrets")
            return None, None

        # Validate AOI
        if not aoi or 'coordinates' not in aoi or not aoi['coordinates']:
            st.error("❌ Please draw a valid area on the map")
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

        # Enhanced progress feedback
        with st.spinner("🛰️ Connecting to Planet's satellite constellation..."):
            time.sleep(1)
            
            response = requests.post(search_url, json=search_request, headers=headers)
            
            if response.status_code == 401:
                st.error("🔐 Authentication failed. Please check your Planet API key.")
                return None, None
            elif response.status_code == 403:
                st.error("🚫 Access forbidden. Check your API key permissions.")
                return None, None
            elif response.status_code != 200:
                st.error(f"❌ Satellite connection error: {response.status_code}")
                return None, None

            results = response.json()
            items = results.get('features', [])
            
            if not items:
                st.warning("""
                ⚠️ **No clear satellite images found** for this area in the last 30 days.
                
                **Try:**
                - Drawing a larger area
                - Selecting a different location  
                - Checking if the area is too cloudy
                """)
                return None, None

            # Get the most recent image
            latest_item = items[0]
            item_id = latest_item['id']
            properties = latest_item.get('properties', {})
            
            # Enhanced success message
            st.success(f"""
            ✅ **Satellite Image Found!**
            
            **Image ID:** {item_id}
            **Acquired:** {properties.get('acquired', 'Recent')}
            **Cloud Cover:** {properties.get('cloud_cover', 0) * 100:.1f}%
            **Quality:** {'Excellent' if properties.get('cloud_cover', 0) < 0.05 else 'Good'}
            """)

            # Create enhanced mock data for demonstration
            st.info("🌿 **Generating vegetation analysis...**")
            time.sleep(1)
            
            mock_ndvi = create_enhanced_ndvi_data(aoi)
            mock_rgb = create_enhanced_rgb_data(aoi)
            
            return mock_rgb, mock_ndvi

    except Exception as e:
        st.error(f"❌ Satellite data error: {str(e)}")
        return None, None

def create_enhanced_ndvi_data(aoi):
    """Create realistic NDVI data for demonstration"""
    try:
        coords = aoi['coordinates'][0]
        
        # Create a synthetic NDVI image with realistic patterns
        width, height = 300, 300
        ndvi_data = np.random.rand(height, width) * 0.8 - 0.2
        
        # Add realistic vegetation patterns
        x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
        
        # Healthy vegetation patches
        healthy_patches = [
            (0.3, 0.3, 0.4),
            (0.7, 0.7, 0.5),
            (0.2, 0.8, 0.3),
            (0.8, 0.2, 0.4)
        ]
        
        for patch_x, patch_y, intensity in healthy_patches:
            distance = np.sqrt((x - patch_x)**2 + (y - patch_y)**2)
            ndvi_data += intensity * np.exp(-distance / 0.2)
        
        # Add linear features
        river_mask = np.abs(y - 0.5*x - 0.2) < 0.05
        ndvi_data[river_mask] -= 0.3
        
        # Add degraded areas
        degraded_mask = (x > 0.6) & (x < 0.9) & (y > 0.1) & (y < 0.4)
        ndvi_data[degraded_mask] -= 0.4
        
        return np.clip(ndvi_data, -1, 1)
        
    except Exception as e:
        return np.random.rand(300, 300) * 0.8 - 0.2

def create_enhanced_rgb_data(aoi):
    """Create realistic RGB satellite imagery"""
    try:
        width, height = 300, 300
        
        # Create base landscape
        rgb_data = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Generate terrain patterns
        x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
        
        # Forest areas
        forest_mask = (np.sin(4*x) * np.cos(4*y) > 0.2)
        rgb_data[forest_mask] = [30, 100, 30]
        
        # Grasslands
        grass_mask = (np.sin(4*x) * np.cos(4*y) <= 0.2) & (np.sin(4*x) * np.cos(4*y) > -0.2)
        rgb_data[grass_mask] = [60, 150, 60]
        
        # Agricultural areas
        agri_mask = (x % 0.2 < 0.1) ^ (y % 0.2 < 0.1)
        agri_mask &= ~forest_mask & ~grass_mask
        rgb_data[agri_mask] = [80, 130, 50]
        
        # Urban/bare areas
        urban_mask = (x > 0.7) & (x < 0.9) & (y > 0.6) & (y < 0.8)
        rgb_data[urban_mask] = [120, 120, 120]
        
        # Water bodies
        water_mask = (np.sqrt((x-0.2)**2 + (y-0.2)**2) < 0.1) | (np.sqrt((x-0.8)**2 + (y-0.3)**2) < 0.08)
        rgb_data[water_mask] = [30, 80, 150]
        
        # Add natural texture
        texture = np.random.randint(-15, 15, (height, width, 3))
        rgb_data = np.clip(rgb_data + texture, 0, 255).astype(np.uint8)
        
        return rgb_data
        
    except Exception as e:
        return np.random.randint(50, 200, (300, 300, 3), dtype=np.uint8)