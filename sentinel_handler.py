import streamlit as st
import numpy as np
from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    MimeType,
    bbox_to_dimensions,
    BBox
)
from skimage.exposure import rescale_intensity

# --- Configuration ---
def configure_sentinel_hub():
    """Configures the Sentinel Hub API using credentials."""
    config = SHConfig()
    # For local development, set your credentials here.
    # For deployment, you would use Streamlit Secrets like st.secrets["..."]
    # IMPORTANT: Replace "YOUR_CLIENT_ID" and "YOUR_CLIENT_SECRET" below
    config.sh_client_id = "YOUR_CLIENT_ID" 
    config.sh_client_secret = "YOUR_CLIENT_SECRET"
    
    if not config.sh_client_id or not config.sh_client_secret:
        st.error("Sentinel Hub credentials are not configured. Please add them.")
        return None
    return config

# --- Data Fetching ---
def get_sentinel_data(aoi, time_interval=("2025-07-01", "2025-10-11")):
    """
    Fetches True Color and NDVI data from Sentinel Hub for a given AOI.
    """
    config = configure_sentinel_hub()
    if not config:
        return None, None
        
    try:
        # 1. Define the geographical bounding box from the drawn AOI
        coords = aoi['coordinates'][0]
        min_lon, max_lon = min(p[0] for p in coords), max(p[0] for p in coords)
        min_lat, max_lat = min(p[1] for p in coords), max(p[1] for p in coords)
        bbox = BBox(bbox=[min_lon, min_lat, max_lon, max_lat], crs="EPSG:4326")
        size = bbox_to_dimensions(bbox, resolution=10)

        # 2. Define an "evalscript" to tell Sentinel Hub what to calculate
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: [{ bands: ["B02", "B03", "B04", "B08"], units: "DN" }],
                output: [
                    { id: "default", bands: 3, sampleType: "UINT8" }, // True Color Image
                    { id: "ndvi", bands: 1, sampleType: "FLOAT32" }    // NDVI Data
                ]
            };
        }
        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            const stretch = s => (s / 3000) * 255; // Normalize true color for better viewing
            return {
                default: [stretch(sample.B04), stretch(sample.B03), stretch(sample.B02)],
                ndvi: [ndvi]
            };
        }
        """

        # 3. Create the request to Sentinel Hub
        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=time_interval,
            )],
            responses=[
                SentinelHubRequest.output_response("default", MimeType.PNG),
                SentinelHubRequest.output_response("ndvi", MimeType.TIFF),
            ],
            bbox=bbox, size=size, config=config,
        )
        
        # 4. Execute the request and get the image arrays
        response = request.get_data()[0]
        true_color_image = response['default.png']
        ndvi_image = response['ndvi.tif']
        
        # Improve contrast for a better visual
        true_color_image = rescale_intensity(true_color_image, out_range='uint8')

        return true_color_image, ndvi_image
    except Exception as e:
        st.error(f"Failed to get data from Sentinel Hub: {e}")
        return None, None