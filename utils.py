import numpy as np
import pandas as pd
from datetime import datetime

def classify_ndvi(ndvi_array, threshold=0.2):
    """
    Classifies NDVI data into 'Healthy' and 'Degraded' based on a threshold.
    """
    # Replace no-data values with NaN to ignore them in calculations
    ndvi_array[ndvi_array == -9999] = np.nan

    degraded_pixels = np.sum(ndvi_array < threshold)
    healthy_pixels = np.sum(ndvi_array >= threshold)
    total_pixels = degraded_pixels + healthy_pixels

    if total_pixels == 0:
        return 0.0, None

    degradation_percentage = (degraded_pixels / total_pixels) * 100
    
    # Create a classified array for potential future visualization
    classified_array = np.zeros(ndvi_array.shape)
    classified_array[ndvi_array >= threshold] = 1  # Healthy

    return degradation_percentage, classified_array

def create_report_csv(aoi, degradation_percentage, threshold=0.2):
    """
    Generates a comprehensive CSV report.
    """
    # Get the bounding box of the AOI
    coords = aoi['coordinates'][0]
    min_lon = min(p[0] for p in coords)
    max_lon = max(p[0] for p in coords)
    min_lat = min(p[1] for p in coords)
    max_lat = max(p[1] for p in coords)
    
    # Calculate area (approximate)
    area_sq_km = approximate_area(min_lon, max_lon, min_lat, max_lat)
    
    # Health assessment
    if degradation_percentage < 10:
        health_status = "Excellent"
        recommendation = "Maintain current practices"
    elif degradation_percentage < 25:
        health_status = "Good" 
        recommendation = "Monitor vegetation health"
    elif degradation_percentage < 40:
        health_status = "Moderate"
        recommendation = "Implement conservation measures"
    else:
        health_status = "Poor"
        recommendation = "Urgent restoration needed"

    data = {
        'Metric': [
            'Report Generated',
            'Land Health Status',
            'Vegetation Health Score',
            'Degraded Area Percentage', 
            'Healthy Area Percentage',
            'NDVI Analysis Threshold',
            'Approximate Area (sq km)',
            'Bounding Box Min Longitude',
            'Bounding Box Max Longitude', 
            'Bounding Box Min Latitude',
            'Bounding Box Max Latitude',
            'Recommended Action',
            'Analysis Confidence'
        ],
        'Value': [
            datetime.now().strftime('%Y-%m-%d %H:%M