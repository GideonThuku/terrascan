import streamlit as st
import folium
from streamlit_folium import st_folium
import planet_handler as data_handler
import utils
import numpy as np
from PIL import Image
import time

# --- MOBILE CSS WITH ENHANCED STYLING ---
def load_css():
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        .stButton button {
            width: 100%;
            font-size: 16px;
        }
        /* Improve mobile touch targets */
        .stButton button, .stDownloadButton button, .stTab button {
            min-height: 44px;
        }
        /* Better mobile scrolling */
        .main .block-container {
            overflow-x: hidden;
        }
        /* Simplify headers for mobile */
        h1, h2, h3 {
            word-wrap: break-word;
        }
    }
    
    /* Always show pointer cursor for buttons */
    .stButton button {
        cursor: pointer;
    }
    
    /* Better tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #262730;
        border-radius: 4px 4px 0px 0px;
    }
    
    /* Custom header styling */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #4CAF50, #45a049);
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Team credits styling */
    .team-credits {
        text-align: center;
        padding: 0.5rem;
        background-color: #262730;
        border-radius: 8px;
        margin: 1rem 0;
        font-style: italic;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Success message styling */
    .stSuccess {
        border-left: 4px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# Load CSS
load_css()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TerraScan - Land Health Analyzer",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TEAM CREDITS ---
st.markdown("""
<div class="main-header">
    <h1>🛰️ TerraScan</h1>
    <h3>AI-Powered Land Health Analysis</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="team-credits">
    <p>🌟 Developed with ❤️ by <strong>Rosemary Emeli</strong> and <strong>Gideon Thuku</strong></p>
</div>
""", unsafe_allow_html=True)

# --- APP STATE ---
if 'aoi' not in st.session_state:
    st.session_state.aoi = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# --- INTERACTIVE TUTORIAL ---
with st.expander("🎯 How to Use TerraScan (Quick Start Guide)", expanded=False):
    st.markdown("""
    **🚀 3 Simple Steps to Analyze Land Health:**
    
    1. **🗺️ Draw Area** - Use the drawing tools on the map to select your region of interest
    2. **📊 Set Sensitivity** - Adjust the NDVI slider to define vegetation health threshold
    3. **🔍 Analyze** - Click the analyze button to get instant satellite insights
    
    **💡 Pro Tips:**
    - Draw larger areas for more accurate results
    - Lower NDVI values detect more degradation
    - Try different areas to compare land health
    """)

# --- INTERACTIVE CONTROLS SECTION ---
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("🎛️ Analysis Controls")
    
    # NDVI Threshold with visual indicators
    ndvi_threshold = st.slider(
        "**Vegetation Health Sensitivity**", 
        min_value=0.0, max_value=0.5, value=0.2, step=0.05,
        help="🔍 Lower values = more sensitive to degradation | Higher values = stricter health criteria"
    )
    
    # Visual indicator for threshold
    if ndvi_threshold < 0.1:
        threshold_status = "🟢 Very Sensitive (Detects slight degradation)"
    elif ndvi_threshold < 0.2:
        threshold_status = "🟡 Sensitive (Balanced detection)"
    elif ndvi_threshold < 0.3:
        threshold_status = "🟠 Moderate (Detects significant degradation)"
    else:
        threshold_status = "🔴 Strict (Only detects severe degradation)"
    
    st.info(f"**Current Setting:** {threshold_status}")

with col2:
    st.subheader("🛠️ Actions")
    analyze_button = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
    
    # Add a quick demo button
    demo_button = st.button("🎮 Quick Demo", use_container_width=True, help="Try with sample data")

with col3:
    st.subheader("📊 History")
    if st.session_state.analysis_history:
        st.info(f"📈 Analyses performed: {len(st.session_state.analysis_history)}")
    else:
        st.info("📊 No analyses yet")

# --- INTERACTIVE MAP SECTION ---
st.markdown("---")
st.subheader("🗺️ Select Your Area of Interest")

# Map with better default location
m = folium.Map(location=[-1.2921, 36.8219], zoom_start=6, tiles="CartoDB positron")  # Centered on Kenya

# Add drawing tools with better styling
folium.plugins.Draw(
    export=False,
    draw_options={
        'polyline': False,
        'polygon': True,
        'rectangle': True,
        'circle': False,
        'marker': False,
        'circlemarker': False,
        'polygon': {
            'allowIntersection': False,
            'showArea': True,
            'drawError': {'color': '#e1e100', 'message': 'Oops! That area looks too complex.'},
            'shapeOptions': {'color': '#4CAF50', 'fillColor': '#4CAF50'}
        },
        'rectangle': {
            'shapeOptions': {'color': '#4CAF50', 'fillColor': '#4CAF50'}
        }
    },
    edit_options={'edit': True}
).add_to(m)

# Add some helpful markers for common locations in Kenya
common_locations = [
    ["Nairobi", -1.2921, 36.8219],
    ["Mombasa", -4.0435, 39.6682],
    ["Kisumu", -0.1022, 34.7617],
    ["Nakuru", -0.3031, 36.0800]
]

for location in common_locations:
    folium.Marker(
        [location[1], location[2]],
        popup=f"<b>{location[0]}</b><br>Click and draw around this area",
        tooltip=f"Analyze {location[0]} region",
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

map_data = st_folium(m, height=400, width=None, key="main_map")

# Handle map interactions
if map_data and map_data.get("all_drawings"):
    st.session_state.aoi = map_data["all_drawings"][0]['geometry']
    st.success("✅ **Area Captured!** Ready for analysis. Click 'Start Analysis' above!")
    
    # Show area info
    coords = st.session_state.aoi['coordinates'][0]
    area_info = f"**Selected Area:** {len(coords)} boundary points"
    st.info(area_info)

# Handle demo button
if demo_button:
    st.session_state.aoi = {
        "type": "Polygon",
        "coordinates": [[
            [36.6813, -1.1821],
            [36.6813, -1.3821],
            [37.0813, -1.3821],
            [37.0813, -1.1821],
            [36.6813, -1.1821]
        ]]
    }
    st.success("🎮 **Demo Mode Activated!** Sample Nairobi area loaded. Click 'Start Analysis'!")

# --- ANALYSIS SECTION WITH PROGRESS INDICATORS ---
st.markdown("---")
st.subheader("📊 Analysis Results")

if analyze_button:
    if st.session_state.aoi:
        # Create a progress container
        progress_container = st.container()
        
        with progress_container:
            # Step 1: Connecting to satellite
            st.info("🛰️ **Step 1:** Connecting to Planet satellite network...")
            progress_bar = st.progress(0)
            
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            
            # Step 2: Fetching data
            st.info("📡 **Step 2:** Downloading latest satellite imagery...")
            progress_bar = st.progress(0)
            
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            
            # Step 3: Processing data
            st.info("🔍 **Step 3:** Analyzing vegetation health patterns...")
            
            with st.spinner("Processing NDVI data and calculating land health metrics..."):
                true_color, ndvi_array = data_handler.get_planet_data(st.session_state.aoi)
                
                if ndvi_array is not None and true_color is not None:
                    degradation_percent, classified_array = utils.classify_ndvi(ndvi_array, ndvi_threshold)
                    
                    # Store results
                    st.session_state.analysis_results = {
                        "degradation_percent": degradation_percent,
                        "true_color_image": true_color,
                        "ndvi_array": ndvi_array,
                        "classified_array": classified_array,
                        "timestamp": time.time(),
                        "threshold": ndvi_threshold
                    }
                    
                    # Add to history
                    st.session_state.analysis_history.append({
                        "degradation": degradation_percent,
                        "threshold": ndvi_threshold,
                        "timestamp": time.time()
                    })
                    
                    st.success("✅ **Analysis Complete!** Scroll down to view results.")
                else:
                    st.error("❌ **Analysis Failed** - Could not retrieve satellite data. Please try a different area.")
                    st.session_state.analysis_results = None
    else:
        st.warning("⚠️ **Please select an area first!** Use the drawing tools on the map above.")

# --- INTERACTIVE RESULTS DISPLAY ---
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    degradation = results['degradation_percent']
    healthy_percent = 100 - degradation
    
    st.markdown("---")
    st.subheader("🎯 Analysis Insights")
    
    # Key metrics with emojis and colors
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if degradation < 20:
            emoji = "💚"
            color = "green"
        elif degradation < 40:
            emoji = "💛"
            color = "orange"
        else:
            emoji = "❤️"
            color = "red"
            
        st.metric(
            label=f"{emoji} Land Health Score",
            value=f"{healthy_percent:.0f}%",
            delta=f"{healthy_percent - 50:.1f}% vs average",
            delta_color="normal" if healthy_percent >= 50 else "inverse"
        )
    
    with col2:
        st.metric(
            label="🌱 Healthy Vegetation",
            value=f"{healthy_percent:.1f}%",
            help="Area with good vegetation cover"
        )
    
    with col3:
        st.metric(
            label="🏜️ Degraded Area", 
            value=f"{degradation:.1f}%",
            help="Area needing attention"
        )
    
    with col4:
        st.metric(
            label="⚙️ Sensitivity",
            value=f"NDVI {ndvi_threshold}",
            help="Current detection threshold"
        )
    
    # Health assessment
    if degradation < 10:
        assessment = "💚 **Excellent Land Health** - Vegetation is thriving!"
        recommendation = "Maintain current land management practices."
    elif degradation < 25:
        assessment = "💛 **Good Land Health** - Minor areas need attention"
        recommendation = "Monitor vegetation and consider soil conservation."
    elif degradation < 40:
        assessment = "🟠 **Moderate Degradation** - Significant areas affected"
        recommendation = "Implement restoration practices and reduce pressure."
    else:
        assessment = "❤️ **High Degradation** - Urgent action needed"
        recommendation = "Consider intensive restoration and conservation measures."
    
    st.info(f"**Assessment:** {assessment}")
    st.warning(f"**Recommendation:** {recommendation}")
    
    # Interactive visualization tabs
    st.markdown("---")
    st.subheader("📷 Satellite Insights")
    
    tab1, tab2, tab3 = st.tabs(["🌱 Vegetation Health Map", "🖼️ Satellite View", "📈 Compare Results"])
    
    with tab1:
        st.markdown("**Normalized Difference Vegetation Index (NDVI) Analysis**")
        ndvi_display = results['ndvi_array']
        
        if ndvi_display is not None:
            # Create enhanced visualization
            ndvi_min = np.nanmin(ndvi_display)
            ndvi_max = np.nanmax(ndvi_display)
            ndvi_normalized = (ndvi_display - ndvi_min) / (ndvi_max - ndvi_min)
            ndvi_normalized = np.nan_to_num(ndvi_normalized, nan=0.0)
            
            # Convert to PIL Image
            ndvi_image = Image.fromarray((ndvi_normalized * 255).astype(np.uint8))
            st.image(ndvi_image, use_column_width=True, 
                    caption=f"🌿 **Vegetation Health Map** | NDVI Range: {ndvi_min:.2f} to {ndvi_max:.2f}")
            
            # Interactive legend
            st.markdown("""
            **🎨 Color Legend:**
            - 💚 **Bright Green**: Healthy, dense vegetation (High NDVI)
            - 💛 **Light Green**: Moderate vegetation cover  
            - 🟡 **Yellow**: Sparse vegetation
            - 🟠 **Orange**: Stressed vegetation
            - ❤️ **Red/Dark**: Bare soil or degraded areas
            """)
    
    with tab2:
        st.markdown("**True Color Satellite Imagery**")
        if results['true_color_image'] is not None:
            st.image(results['true_color_image'], use_column_width=True, 
                    caption="🛰️ **Recent Satellite View** from Planet Labs")
            st.info("This is how the area actually looks from space!")
        else:
            st.warning("Satellite image not available")
    
    with tab3:
        st.markdown("**📊 Analysis History & Comparison**")
        if len(st.session_state.analysis_history) > 1:
            st.write("**Recent Analyses:**")
            for i, analysis in enumerate(st.session_state.analysis_history[-5:]):  # Show last 5
                st.write(f"{i+1}. Degradation: {analysis['degradation']:.1f}% | Threshold: {analysis['threshold']}")
        else:
            st.info("Run more analyses to see comparison data")
        
        # Quick re-analysis with different threshold
        st.markdown("**🔧 Try Different Sensitivity:**")
        new_threshold = st.slider("Adjust NDVI threshold to see different results", 
                                0.0, 0.5, ndvi_threshold, 0.05, key="comparison_slider")
        
        if new_threshold != ndvi_threshold:
            new_degradation, _ = utils.classify_ndvi(results['ndvi_array'], new_threshold)
            st.metric("New Degradation Estimate", f"{new_degradation:.1f}%", 
                     delta=f"{new_degradation - degradation:.1f}% change")
    
    # Export section
    st.markdown("---")
    st.subheader("📤 Export & Share")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        csv_data = utils.create_report_csv(st.session_state.aoi, degradation)
        st.download_button(
           label="📥 Download Detailed Report (CSV)",
           data=csv_data,
           file_name=f"terrascan_report_{time.strftime('%Y%m%d_%H%M')}.csv",
           mime="text/csv",
           use_container_width=True
        )
    
    with col_export2:
        st.button("🔄 Analyze New Area", use_container_width=True, 
                 help="Clear current results and start fresh")
    
else:
    # Welcome state
    st.markdown("---")
    st.info("""
    **👋 Welcome to TerraScan!**
    
    Ready to analyze land health? Here's what you can do:
    
    🎯 **Quick Start:** Click the **Quick Demo** button for instant results
    🗺️ **Custom Analysis:** Draw your own area on the map above
    📊 **Get Insights:** View vegetation health, degradation levels, and recommendations
    
    *Developed with cutting-edge satellite technology and AI analysis*
    """)

# --- ENHANCED FOOTER WITH CREDITS ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: #262730; border-radius: 10px;'>
    <h4>🛰️ TerraScan v2.0</h4>
    <p><strong>Powered by Planet API | Built with Streamlit ⚡</strong></p>
    <p style='font-size: 0.9em; color: #888;'>
        💻 Developed with passion by <strong>Rosemary Emeli</strong> and <strong>Gideon Thuku</strong><br>
        🎯 Making land health monitoring accessible to everyone
    </p>
</div>
""", unsafe_allow_html=True)