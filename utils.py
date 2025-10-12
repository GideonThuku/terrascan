import numpy as np
import pandas as pd
from datetime import datetime


def approximate_area(min_lon, max_lon, min_lat, max_lat):
    """
    Approximate area (in square km) using a rough conversion.
    """
    km_per_deg_lat = 111  # Approximate conversion
    km_per_deg_lon = 111 * np.cos(np.radians((min_lat + max_lat) / 2))
    width = (max_lon - min_lon) * km_per_deg_lon
    height = (max_lat - min_lat) * km_per_deg_lat
    return abs(width * height)


def classify_ndvi(ndvi_array, threshold=0.2):
    """
    Classifies NDVI data into 'Healthy' and 'Degraded' based on a threshold.
    """
    ndvi_array = np.array(ndvi_array, dtype=float)
    ndvi_array[ndvi_array == -9999] = np.nan

    degraded_pixels = np.sum(ndvi_array < threshold)
    healthy_pixels = np.sum(ndvi_array >= threshold)
    total_pixels = degraded_pixels + healthy_pixels

    if total_pixels == 0:
        return 0.0, None

    degradation_percentage = (degraded_pixels / total_pixels) * 100

    classified_array = np.zeros(ndvi_array.shape)
    classified_array[ndvi_array >= threshold] = 1  # Healthy

    return degradation_percentage, classified_array


def create_report_csv(aoi, degradation_percentage, threshold=0.2):
    """
    Generates a comprehensive CSV report and returns it as a string.
    """
    coords = aoi['coordinates'][0]
    min_lon = min(p[0] for p in coords)
    max_lon = max(p[0] for p in coords)
    min_lat = min(p[1] for p in coords)
    max_lat = max(p[1] for p in coords)

    area_sq_km = approximate_area(min_lon, max_lon, min_lat, max_lat)

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
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            health_status,
            f"{100 - degradation_percentage:.2f}",
            f"{degradation_percentage:.2f}",
            f"{100 - degradation_percentage:.2f}",
            threshold,
            f"{area_sq_km:.2f}",
            min_lon,
            max_lon,
            min_lat,
            max_lat,
            recommendation,
            "High"
        ]
    }

    df = pd.DataFrame(data)
    # Return the CSV content as a string for the download button
    return df.to_csv(index=False).encode('utf-8')