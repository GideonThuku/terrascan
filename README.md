# 🛰️ TerraScan: AI-Powered Land Health Analysis

**LIVE DEMO:** [https://terrascanafritech.streamlit.app/](https://terrascanafritech.streamlit.app/)

A project by **Gideon Thuku** and **Rosemary Emeli**.

---

## 📖 About The Project

TerraScan is a user-friendly web application designed to analyze the health of land and vegetation using up-to-date satellite imagery.  
It helps farmers, environmentalists, researchers, and land managers quickly assess land degradation, monitor crop health, and make informed decisions for sustainable land management.

The core of our analysis is the **Normalized Difference Vegetation Index (NDVI)**, a trusted scientific method to measure vegetation greenness and vitality.  
By processing recent satellite data, TerraScan provides a clear picture of how healthy a specific area of land is, identifies areas under stress, and offers practical recommendations.

---

## ✨ Key Features

- **Interactive Map Selection:** Draw a custom area of interest directly on an interactive map.  
- **Real-time Satellite Data:** Fetches the latest imagery from the Planet satellite network.  
- **Advanced Vegetation Analysis:** Automatically calculates NDVI for detailed vegetation health.  
- **Custom Sensitivity:** Adjust detection from minor vegetation stress to severe degradation.  
- **Rich Visualizations:**
  - Health Map showing vegetation status.  
  - True Color Image from satellite data.  
- **Actionable Insights:** Professional recommendations for land management.  
- **Data Export:** Download full analysis reports in CSV format.

---

## ⚙️ How It Works

1. **Select Area:** Draw a polygon or rectangle to define the Area of Interest (AOI).  
2. **Set Parameters:** Adjust NDVI threshold for sensitivity.  
3. **Fetch Data:** Connects to the Planet API for recent satellite imagery.  
4. **Process Imagery:** Calculates NDVI per pixel.  
5. **Classify Land:** Categorizes vegetation as “Healthy” or “Needs Attention.”  
6. **Display Results:** Visual maps, health scores, and recommendations appear on dashboard.

---

## 💻 Technology Stack

- **Language:** Python  
- **Framework:** Streamlit  
- **Data Processing:** Pandas, NumPy  
- **Mapping:** Folium, streamlit-folium  
- **Satellite Provider:** Planet API  
- **Visualization:** Pillow, Matplotlib  

---

## 🚀 Getting Started (Running Locally)

### Prerequisites
- Python 3.8+  
- pip  
- Planet API key

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/terrascan.git
cd terrascan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add Planet API key
mkdir .streamlit
echo 'PLANET_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"' > .streamlit/secrets.toml

# Run the app
streamlit run app.py
```

---

## 🗺️ How to Use

1. **Select Your Area:** Draw your region of interest on the map.  
2. **Set Sensitivity:** Adjust slider to define NDVI sensitivity.  
3. **Start Analysis:** Click “Start Satellite Analysis.”  
4. **Review Results:** View health score, maps, and insights.  
5. **Download Report:** Export CSV report.

---

## 🙏 Acknowledgements

- Developed by **Gideon Thuku** and **Rosemary Emeli**  
- Satellite data powered by **Planet.com**  
- Built with **Streamlit**  
- Mapping by **Folium**

© 2025 TerraScan by Gideon and Rose, PLP Academy
