import streamlit as st
import folium
from streamlit_folium import st_folium
import sentinel_handler as data_handler # MODIFIED: Use the new sentinel_handler
import utils

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TerraScan",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- APP STATE ---
# Initialize session state variables to persist data across reruns
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
    
    **2. Set Threshold:** Adjust the NDVI slider to define what you consider 'degraded' vegetation. Lower values typically indicate stressed or sparse vegetation.
    
    **3. Run Analysis:** Click the button to fetch and process the satellite data.
    """)
    
    ndvi_threshold = st.slider(
        "Degradation Threshold (NDVI)", 
        min_value=0.0, max_value=0.5, value=0.2, step=0.05,
        help="Pixels with NDVI below this value will be classified as 'Degraded'."
    )
    
    analyze_button = st.button("Analyze Land Health", type="primary", use_container_width=True)

# --- MAIN CONTENT ---
# Create two columns for map and results
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Area of Interest (AOI)")
    
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

    map_data = st_folium(m, height=500, width=700)

    if map_data and map_data.get("all_drawings"):
        st.session_state.aoi = map_data["all_drawings"][0]['geometry']

with col2:
    st.subheader("Analysis Results")
    
    if analyze_button:
        if st.session_state.aoi:
            with st.spinner("Accessing satellite archives... Please wait."):
                # MODIFIED: Call the new Sentinel Hub data handler
                true_color, ndvi_array = data_handler.get_sentinel_data(st.session_state.aoi)
                
                if ndvi_array is not None:
                    # Perform classification using the utility function
                    degradation_percent, _ = utils.classify_ndvi(ndvi_array, ndvi_threshold)
                    
                    # Store results in session state
                    st.session_state.analysis_results = {
                        "degradation_percent": degradation_percent,
                        "true_color_image": true_color,
                        "ndvi_array": ndvi_array 
                    }
                    st.success("Analysis complete!")
                else:
                    st.error("Could not retrieve data. Please check your AOI or credentials.")
                    st.session_state.analysis_results = None # Clear old results on error
        else:
            st.warning("Please draw an area on the map first.")

    # Display results if they exist in the session state
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        degradation = results['degradation_percent']

        st.metric(
            label="Degraded Land",
            value=f"{degradation:.2f} %",
            delta=f"{degradation - 50:.2f} % vs 50% baseline", # Example delta
            delta_color="inverse"
        )
        
        st.info(f"Based on an NDVI threshold of **{ndvi_threshold}**")

        # MODIFIED: Display images directly from the NumPy arrays
        tab1, tab2 = st.tabs(["Vegetation Index (NDVI)", "True Color"])
        
        with tab1:
            st.markdown("**Normalized Difference Vegetation Index**")
            # Display the NDVI array directly, using a built-in colormap
            st.image(
                results['ndvi_array'], 
                caption="Higher values (brighter) indicate healthier vegetation.",
                clamp=True, # Scales colors from 0-1 for better visualization
                use_column_width=True
            )

        with tab2:
            st.markdown("**Recent True Color Image**")
            st.image(
                results['true_color_image'], 
                caption="A composite true-color image from recent satellite passes.",
                use_column_width=True
            )
            
        # Generate and provide download button for the CSV report
        csv_data = utils.create_report_csv(st.session_state.aoi, degradation)
        st.download_button(
           label="Download Report (CSV)",
           data=csv_data,
           file_name="terrascan_report.csv",
           mime="text/csv",
           use_container_width=True
        )
    else:
        st.info("Results will be displayed here after analysis.")