import ee
import numpy as np

# Trigger the authentication flow.
ee.Initialize()

def get_ndvi_data(aoi, start_date='2025-07-01', end_date='2025-10-01'):
    """
    Fetches, processes, and returns NDVI data for a given Area of Interest (AOI).
    
    Args:
        aoi (dict): A dictionary representing the AOI geometry from GeoJSON.
        start_date (str): The start date for the image collection.
        end_date (str): The end date for the image collection.

    Returns:
        tuple: A tuple containing:
            - A GEE map ID for the NDVI visualization.
            - A NumPy array of the raw NDVI data for analysis.
            - A GEE map ID for the true-color image visualization.
    """
    try:
        geometry = ee.Geometry.Polygon(aoi['coordinates'])

        # Use Sentinel-2 data, filter by date, AOI, and cloud cover.
        collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                      .filterDate(start_date, end_date)
                      .filterBounds(geometry)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                      .median()) # Use median to get a clear composite image

        # Define bands for visualization and calculation
        vis_params_true_color = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
        
        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        # For Sentinel-2, NIR is B8 and Red is B4.
        ndvi = collection.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # Define visualization palette for NDVI
        ndvi_palette = ['#ff0000', '#ffff00', '#00ff00'] # Red (low) -> Yellow -> Green (high)
        vis_params_ndvi = {'min': -0.2, 'max': 0.8, 'palette': ndvi_palette}

        # Clip images to the AOI for cleaner processing
        true_color_clipped = collection.clip(geometry)
        ndvi_clipped = ndvi.clip(geometry)

        # Get map IDs to generate tile URLs for Folium
        map_id_ndvi = ndvi_clipped.getMapId(vis_params_ndvi)
        map_id_true_color = true_color_clipped.getMapId(vis_params_true_color)
        
        # To get the raw data for NumPy analysis, we need to sample the region.
        # This is an intensive operation, so we reduce the scale for performance in the MVP.
        ndvi_array_data = ndvi_clipped.sampleRectangle(region=geometry, defaultValue=-9999)
        ndvi_band_data = ndvi_array_data.get('NDVI')
        
        # Convert to a NumPy array
        numpy_array = np.array(ndvi_band_data.getInfo())
        
        return map_id_ndvi, numpy_array, map_id_true_color

    except Exception as e:
        print(f"An error occurred in GEE Handler: {e}")
        return None, None, None