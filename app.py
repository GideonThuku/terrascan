import streamlit as st
import folium
from streamlit_folium import st_folium
import planet_handler as data_handler  # CHANGED: Use Planet handler
import utils
import numpy as np
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TerraScan",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- APP STATE ---
if 'aoi' not in st.session_state:
    st.session_state.aoi = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# --- UI LAYOUT ---
st.title("🛰️ TerraScan")
st.markdown("### AI-powered vigilance for land health.")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Controls")
    st.markdown("""
    **1. Draw Your Area:** Use the drawing tools on the map to define the area you want to analyze.
    
    **2. Set Threshold:** Adjust the NDVI slider to define what you consider 'degraded' vegetation.
    
    **3. Run Analysis:** Click the button to fetch and process the satellite data.
    """)
    
    ndvi_threshold = st.slider(
        "Degradation Threshold (NDVI)", 
        min_value=0.0, max_value=0.5, value=0.2, step=0.05,
        help="Pixels with NDVI below this value will be classified as 'Degraded'."
    )
    
    analyze_button = st.button("Analyze Land Health", type="primary", use_container_width=True)

# --- MAIN CONTENT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Area of Interest (AOI)")
    
    # Center map on Kenya
    m = folium.Map(location=[-0.0236, 37.9062], zoom_start=7, tiles="CartoDB positron")

    folium.plugins.Draw(
        export=False,
        draw_options={
            'polyline': False,
            'polygon': True,
            'rectangle': True,
            'circle': False,
            'marker': False,
            'circlemarker': False
        }).add_to(m)

    map_data = st_folium(m, height=500, width=700, key="map")

    if map_data and map_data.get("all_drawings"):
        st.session_state.aoi = map_data["all_drawings"][0]['geometry']
        st.success("✅ Area of Interest captured!")

with col2:
    st.subheader("Analysis Results")
    
    if analyze_button:
        if st.session_state.aoi:
            with st.spinner("🛰️ Accessing Planet satellite imagery... This may take a moment."):
                # CHANGED: Call Planet data handler instead of Sentinel
                true_color, ndvi_array = data_handler.get_planet_data(st.session_state.aoi)
                
                if ndvi_array is not None and true_color is not None:
                    degradation_percent, _ = utils.classify_ndvi(ndvi_array, ndvi_threshold)
                    
                    st.session_state.analysis_results = {
                        "degradation_percent": degradation_percent,
                        "true_color_image": true_color,
                        "ndvi_array": ndvi_array 
                    }
                    st.success("✅ Analysis complete!")
                else:
                    st.error("❌ Could not retrieve satellite data. Please try a different area.")
                    st.session_state.analysis_results = None
        else:
            st.warning("⚠️ Please draw an area on the map first.")

    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        degradation = results['degradation_percent']

        st.metric(
            label="Degraded Land",
            value=f"{degradation:.1f}%",
            help="Percentage of area with NDVI below threshold"
        )
        
        st.info(f"Based on NDVI threshold: **{ndvi_threshold}**")

        # Display images with proper handling
        tab1, tab2 = st.tabs(["🌱 Vegetation Index (NDVI)", "🖼️ True Color"])
        
        with tab1:
            st.markdown("**Normalized Difference Vegetation Index**")
            ndvi_display = results['ndvi_array']
            
            # Normalize NDVI for better visualization
            if ndvi_display is not None:
                # Create a colormap for NDVI
                ndvi_normalized = (ndvi_display - np.nanmin(ndvi_display)) / (np.nanmax(ndvi_display) - np.nanmin(ndvi_display))
                ndvi_normalized = np.nan_to_num(ndvi_normalized, nan=0.0)
                
                # Convert to PIL Image for better display
                ndvi_image = Image.fromarray((ndvi_normalized * 255).astype(np.uint8))
                st.image(ndvi_image, caption="NDVI Map: Brighter areas = healthier vegetation", use_column_width=True)
                
                # Show NDVI value range
                st.caption(f"NDVI range: {np.nanmin(ndvi_display):.2f} to {np.nanmax(ndvi_display):.2f}")
            else:
                st.warning("No NDVI data available")

        with tab2:
            st.markdown("**True Color Satellite Image**")
            if results['true_color_image'] is not None:
                st.image(results['true_color_image'], caption="Satellite image (Planet)", use_column_width=True)
            else:
                st.warning("No true color image available")
            
        # Download report
        csv_data = utils.create_report_csv(st.session_state.aoi, degradation)
        st.download_button(
           label="📥 Download Report (CSV)",
           data=csv_data,
           file_name="terrascan_report.csv",
           mime="text/csv",
           use_container_width=True
        )
    else:
        st.info("👆 Results will appear here after analysis.")

# --- FOOTER ---
st.markdown("---")
st.caption("TerraScan v1.0 | Powered by Planet API 🌍")