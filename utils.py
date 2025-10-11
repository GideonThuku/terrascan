import numpy as np
import pandas as pd

def classify_ndvi(ndvi_array, threshold=0.2):
    """
    Classifies NDVI data into 'Healthy' and 'Degraded' based on a threshold.

    Args:
        ndvi_array (np.array): The input NumPy array containing NDVI values.
        threshold (float): The NDVI value to classify against.

    Returns:
        tuple: A tuple containing:
            - The percentage of degraded land (float).
            - The classified image as a NumPy array (1 for Healthy, 0 for Degraded).
    """
    # Replace no-data values (-9999) with NaN to ignore them in calculations
    ndvi_array[ndvi_array == -9999] = np.nan

    degraded_pixels = np.sum(ndvi_array < threshold)
    healthy_pixels = np.sum(ndvi_array >= threshold)
    total_pixels = degraded_pixels + healthy_pixels

    if total_pixels == 0:
        return 0.0, None

    degradation_percentage = (degraded_pixels / total_pixels) * 100
    
    # Create a classified array for potential future visualization
    classified_array = np.zeros(ndvi_array.shape)
    classified_array[ndvi_array >= threshold] = 1 # Healthy

    return degradation_percentage, classified_array

def create_report_csv(aoi, degradation_percentage):
    """
    Generates a simple CSV report as a string.

    Args:
        aoi (dict): The AOI coordinates.
        degradation_percentage (float): The calculated percentage of degraded land.

    Returns:
        str: A string containing the data in CSV format.
    """
    # Get the bounding box of the AOI
    coords = aoi['coordinates'][0]
    min_lon = min(p[0] for p in coords)
    max_lon = max(p[0] for p in coords)
    min_lat = min(p[1] for p in coords)
    max_lat = max(p[1] for p in coords)

    data = {
        'Metric': ['Degradation Percentage', 'Bounding Box Min Longitude', 'Bounding Box Max Longitude', 'Bounding Box Min Latitude', 'Bounding Box Max Latitude'],
        'Value': [f"{degradation_percentage:.2f}%", min_lon, max_lon, min_lat, max_lat]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')