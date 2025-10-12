import streamlit as st
import folium
from streamlit_folium import st_folium
import planet_handler as data_handler
import streamlit as st
import utils
import numpy as np
from PIL import Image
import time
import matplotlib.cm as cm

# --- ENHANCED CSS WITH DARK GREEN THEME ---
def load_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-green: #1B5E20;
        --secondary-green: #2E7D32;
        --accent-green: #4CAF50;
        --light-green: #E8F5E8;
        --dark-bg: #0E1117;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        .stButton button {
            width: 100%;
            font-size: 16px;
        }
        .stButton button, .stDownloadButton button, .stTab button {
            min-height: 44px;
        }
        .main .block-container {
            overflow-x: hidden;
        }
        h1, h2, h3 {
            word-wrap: break-word;
        }
    }
    
    /* Enhanced header with gradient */
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--primary-green), var(--secondary-green));
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid var(--accent-green);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header h3 {
        color: var(--light-green);
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 0;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, var(--primary-green), transparent);
        padding: 1rem;
        border-radius: 8px;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid var(--accent-green);
    }
    
    .section-header h2 {
        color: white;
        margin: 0;
        font-size: 1.5rem;
    }
    
    /* Step indicators */
    .step-container {
        background-color: var(--dark-bg);
        border: 1px solid var(--secondary-green);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .step-number {
        background-color: var(--accent-green);
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .step-title {
        color: var(--accent-green);
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .step-description {
        color: #CCCCCC;
        line-height: 1.5;
    }
    
    /* Enhanced buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--secondary-green), var(--primary-green));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-green), var(--secondary-green));
    }
    
    /* Success messages */
    .stSuccess {
        border-left: 4px solid var(--accent-green);
        background-color: rgba(76, 175, 80, 0.1);
    }
    
    /* Info boxes */
    .stInfo {
        border-left: 4px solid var(--secondary-green);
        background-color: rgba(46, 125, 50, 0.1);
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: var(--dark-bg);
        border: 1px solid var(--secondary-green);
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, var(--primary-green), var(--dark-bg));
        border-radius: 15px;
        margin-top: 3rem;
        border: 1px solid var(--secondary-green);
    }
    
    .footer-text {
        color: white;
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

# --- ENHANCED HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🛰️ TerraScan</h1>
    <h3>AI-Powered Land Health Analysis</h3>
</div>
""", unsafe_allow_html=True)

# --- APP STATE ---
if 'aoi' not in st.session_state:
    st.session_state.aoi = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# --- COMPREHENSIVE USER GUIDE ---
with st.expander("📚 Complete User Guide - Learn How to Use TerraScan", expanded=True):
    st.markdown("""
    <div class="step-container">
        <div class="step-title"><span class="step-number">1</span> Understanding TerraScan</div>
        <div class="step-description">
        TerraScan uses advanced satellite technology to analyze vegetation health. 
        Our system processes satellite imagery to calculate the NDVI (Normalized Difference Vegetation Index), 
        which measures how green and healthy vegetation is in your selected area.
        </div>
    </div>
    
    <div class="step-container">
        <div class="step-title"><span class="step-number">2</span> Step 1: Select Your Area</div>
        <div class="step-description">
        <strong>How to draw on the map:</strong>
        - Click the <span style="color: #4CAF50;">■ polygon tool</span> or <span style="color: #4CAF50;">□ rectangle tool</span> in the map toolbar
        - Draw a shape around the area you want to analyze
        - Make sure the area is large enough for accurate analysis (at least 1km x 1km)
        - You can edit or delete your drawing if needed
        </div>
    </div>
    
    <div class="step-container">
        <div class="step-title"><span class="step-number">3</span> Step 2: Set Analysis Sensitivity</div>
        <div class="step-description">
        <strong>Understanding NDVI Threshold:</strong>
        - <strong>Low values (0.0-0.1):</strong> Very sensitive - detects even slight vegetation stress
        - <strong>Medium values (0.1-0.2):</strong> Balanced detection - good for general monitoring
        - <strong>High values (0.2+):</strong> Strict - only detects significant degradation
        <br><br>
        <em>Tip: Start with 0.2 and adjust based on your needs</em>
        </div>
    </div>
    
    <div class="step-container">
        <div class="step-title"><span class="step-number">4</span> Step 3: Run Analysis</div>
        <div class="step-description">
        Click the "Start Analysis" button to begin processing. Our system will:
        - Connect to Planet's satellite network
        - Download the latest satellite imagery
        - Calculate vegetation health metrics
        - Generate comprehensive analysis report
        <br><br>
        <strong>Processing time:</strong> Typically 30-60 seconds
        </div>
    </div>
    
    <div class="step-container">
        <div class="step-title"><span class="step-number">5</span> Step 4: Interpret Results</div>
        <div class="step-description">
        <strong>Understanding your results:</strong>
        - <strong>Land Health Score:</strong> Overall vegetation health percentage
        - <strong>Degraded Area:</strong> Percentage needing attention
        - <strong>Vegetation Map:</strong> Visual representation of health patterns
        - <strong>Recommendations:</strong> Actionable insights for land management
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- INTERACTIVE MAP SECTION ---
st.markdown("""
<div class="section-header">
    <h2>🗺️ Step 1: Select Your Analysis Area</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Instructions:** Use the drawing tools in the top-right corner of the map below to select your area of interest.
- Click the **polygon tool** (■) for custom shapes
- Click the **rectangle tool** (□) for rectangular areas
- Draw on the map to define your analysis boundary
""")

# Enhanced map with better styling
m = folium.Map(location=[-1.2921, 36.8219], zoom_start=6, tiles="CartoDB positron")

# Enhanced drawing tools
folium.plugins.Draw(
    export=False,
    draw_options={
        'polyline': False,
        'polygon': {
            'allowIntersection': False,
            'showArea': True,
            'drawError': {'color': '#e1e100', 'message': '⚠️ Please draw a simpler shape'},
            'shapeOptions': {'color': '#1B5E20', 'fillColor': '#1B5E20', 'fillOpacity': 0.3}
        },
        'rectangle': {
            'shapeOptions': {'color': '#1B5E20', 'fillColor': '#1B5E20', 'fillOpacity': 0.3}
        },
        'circle': False,
        'marker': False,
        'circlemarker': False
    },
    edit_options={'edit': True}
).add_to(m)

# Add informative markers for Kenya
kenya_locations = [
    ["Nairobi Capital", -1.2921, 36.8219, "Start here for urban analysis"],
    ["Mombasa Coastal", -4.0435, 39.6682, "Coastal vegetation monitoring"],
    ["Kisumu Western", -0.1022, 34.7617, "Lake region agriculture"],
    ["Nakuru Rift Valley", -0.3031, 36.0800, "Agricultural lands"]
]

for name, lat, lon, description in kenya_locations:
    folium.Marker(
        [lat, lon],
        popup=f"<b>{name}</b><br><em>{description}</em>",
        tooltip=f"Click for info about {name}",
        icon=folium.Icon(color='green', icon='info-sign', prefix='fa')
    ).add_to(m)

# Display the map
map_data = st_folium(m, height=500, width=None, key="main_map")

# Handle map interactions
if map_data and map_data.get("all_drawings"):
    st.session_state.aoi = map_data["all_drawings"][0]['geometry']
    
    # Show area confirmation
    coords = st.session_state.aoi['coordinates'][0]
    area_size = len(coords)
    
    st.success(f"""
    ✅ **Area Successfully Selected!**
    
    - **Boundary Points:** {area_size} coordinates
    - **Status:** Ready for analysis
    - **Next Step:** Set parameters below and click 'Start Analysis'
    """)
    
    # Show quick area stats
    if area_size > 4:  # Basic polygon
        st.info("🗺️ **Tip:** Your area has been captured. For best results, ensure your area covers at least 1 square kilometer.")

# --- ANALYSIS CONTROLS SECTION - MOVED BELOW MAP ---
st.markdown("""
<div class="section-header">
    <h2>🎛️ Step 2: Set Analysis Parameters</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### 📊 Analysis Configuration")
    
    ndvi_threshold = st.slider(
        "**Vegetation Health Sensitivity (NDVI Threshold)**", 
        min_value=0.0, max_value=0.5, value=0.2, step=0.05,
        help="""**How to choose:** - 0.0-0.1: Very sensitive (detects slight stress)
- 0.1-0.2: Balanced (recommended for most areas)  
- 0.2-0.3: Moderate (detects significant issues)
- 0.3-0.5: Strict (only severe degradation)"""
    )
    
    # Visual threshold indicator
    threshold_col1, threshold_col2 = st.columns(2)
    
    with threshold_col1:
        if ndvi_threshold <= 0.1:
            st.success("**Very Sensitive**")
        elif ndvi_threshold <= 0.2:
            st.info("**Balanced**")
        else:
            st.warning("**Strict**")
    
    with threshold_col2:
        st.metric("Current Setting", f"NDVI {ndvi_threshold}")

with col2:
    st.markdown("#### ⚡ Start Analysis")
    analyze_button = st.button("🚀 Start Satellite Analysis", type="primary", use_container_width=True)
    
    st.markdown("#### 🔄 Management")
    if st.button("🔄 Clear Results", use_container_width=True):
        st.session_state.aoi = None
        st.session_state.analysis_results = None
        st.rerun()

# --- ANALYSIS EXECUTION SECTION ---
st.markdown("""
<div class="section-header">
    <h2>🔍 Step 3: Run Satellite Analysis</h2>
</div>
""", unsafe_allow_html=True)

if analyze_button:
    if st.session_state.aoi:
        # Create placeholders for the progress display
        progress_placeholder = st.empty()
        
        # We will use a single bar and a text element for cleaner updates
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Connection (Simulated)
            status_text.info("📡 Step 1/3: Connecting to satellite network...")
            for i in range(33):
                progress_bar.progress(i)
                time.sleep(0.01)

            # Step 2: Data Acquisition (Actual API call happens here)
            status_text.info("🛰️ Step 2/3: Acquiring latest satellite imagery...")
            true_color, ndvi_array = data_handler.get_planet_data(st.session_state.aoi)
            
            # Update progress after the API call returns
            for i in range(33, 67):
                progress_bar.progress(i)
                time.sleep(0.01)

            # Step 3: Processing
            status_text.info("🌿 Step 3/3: Analyzing vegetation health...")
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

                # Finalize progress and show success
                for i in range(67, 101):
                    progress_bar.progress(i)
                    time.sleep(0.01)
                
                # Clear the progress elements and show the final message
                status_text.empty()
                progress_bar.empty()
                progress_placeholder.success("""
                ✅ **Analysis Complete!** Your land health assessment is ready. Scroll down to view the detailed results.
                """)

            else:
                # If data_handler returned None, it means an error occurred
                # The error message is already displayed by data_handler
                status_text.empty()
                progress_bar.empty()
                # We don't need to show another error message here as planet_handler.py does it.
                
        except Exception as e:
            # Catch any unexpected errors during the process
            status_text.empty()
            progress_bar.empty()
            st.error(f"An unexpected error occurred during analysis: {e}")

    else:
        st.warning("""
        ⚠️ **No Area Selected**
        
        Please draw an area on the map above before starting analysis. 
        Use the polygon or rectangle tools to define your region of interest.
        """)

# --- RESULTS DISPLAY SECTION ---
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    degradation = results['degradation_percent']
    healthy_percent = 100 - degradation
    
    st.markdown("""
    <div class="section-header">
        <h2>📊 Step 4: Review Your Analysis Results</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Comprehensive Results Overview
    st.markdown("#### 🎯 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Health score with color coding
        if healthy_percent >= 80:
            score_emoji = "💚"
            score_color = "green"
        elif healthy_percent >= 60:
            score_emoji = "💛" 
            score_color = "orange"
        else:
            score_emoji = "❤️"
            score_color = "red"
            
        st.metric(
            label=f"{score_emoji} Overall Health Score",
            value=f"{healthy_percent:.0f}%",
            delta="Excellent" if healthy_percent >= 80 else "Good" if healthy_percent >= 60 else "Needs Attention",
            delta_color="normal" if healthy_percent >= 60 else "inverse"
        )
    
    with col2:
        st.metric(
            label="🌱 Healthy Vegetation",
            value=f"{healthy_percent:.1f}%",
            help="Area with robust vegetation cover"
        )
    
    with col3:
        st.metric(
            label="🏜️ Areas Needing Attention", 
            value=f"{degradation:.1f}%",
            help="Land showing signs of degradation"
        )
    
    with col4:
        st.metric(
            label="⚡ Analysis Sensitivity",
            value=f"NDVI {ndvi_threshold}",
            help="Detection threshold used"
        )
    
    # Health Assessment & Recommendations
    st.markdown("#### 💡 Professional Assessment")
    
    if degradation < 10:
        assessment = "💚 **Excellent Land Health**"
        details = "Your area shows outstanding vegetation vitality with minimal signs of stress."
        recommendations = [
            "Continue current land management practices",
            "Monitor seasonal changes regularly", 
            "Consider biodiversity enhancement projects"
        ]
    elif degradation < 25:
        assessment = "💛 **Good Land Health**"
        details = "Vegetation is generally healthy with some localized areas needing attention."
        recommendations = [
            "Implement targeted soil conservation",
            "Monitor water availability in dry seasons",
            "Consider selective planting in sparse areas"
        ]
    elif degradation < 40:
        assessment = "🟠 **Moderate Degradation**"
        details = "Significant areas show vegetation stress requiring active management."
        recommendations = [
            "Develop comprehensive restoration plan",
            "Implement soil and water conservation",
            "Reduce grazing pressure if applicable",
            "Monitor progress quarterly"
        ]
    else:
        assessment = "❤️ **High Degradation - Action Needed**"
        details = "Urgent intervention required to prevent further land degradation."
        recommendations = [
            "Immediate soil conservation measures",
            "Professional land restoration consultation",
            "Reduce or eliminate land use pressure",
            "Implement emergency revegetation"
        ]
    
    st.success(f"**Assessment:** {assessment}")
    st.info(f"**Details:** {details}")
    
    st.warning("**📋 Recommended Actions:**")
    for i, recommendation in enumerate(recommendations, 1):
        st.write(f"{i}. {recommendation}")
    
    # Interactive Visualization Tabs
    st.markdown("#### 📷 Detailed Visual Analysis")
    
    tab1, tab2 = st.tabs(["🌱 Vegetation Health Map", "🖼️ Satellite Overview"])
    
    with tab1:
        st.markdown("**Normalized Difference Vegetation Index (NDVI) Analysis**")
        ndvi_display = results['ndvi_array']
        
        if ndvi_display is not None:
            # Enhanced visualization with a safety check
            ndvi_min = np.nanmin(ndvi_display)
            ndvi_max = np.nanmax(ndvi_display)
            
            # Check to prevent division by zero if the data is uniform
            if (ndvi_max - ndvi_min) > 0:
                ndvi_normalized = (ndvi_display - ndvi_min) / (ndvi_max - ndvi_min)
            else:
                # If data is uniform, avoid division and just create a zero array
                ndvi_normalized = np.zeros_like(ndvi_display)

            ndvi_normalized = np.nan_to_num(ndvi_normalized, nan=0.0)
            
            # Convert to PIL Image using a colormap for better visualization
            ndvi_image = Image.fromarray((cm.viridis(ndvi_normalized) * 255).astype(np.uint8))
            
            st.image(ndvi_image, use_column_width=True, 
                    caption=f"**Vegetation Health Visualization** | NDVI Range: {ndvi_min:.3f} to {ndvi_max:.3f}")
            
            # Comprehensive legend
            st.markdown("""
            **🎨 Vegetation Health Color Guide:**
            - **💚 Deep Green:** Excellent health (NDVI 0.6-1.0)
            - **💛 Light Green:** Good health (NDVI 0.3-0.6)  
            - **🟡 Yellow:** Moderate health (NDVI 0.1-0.3)
            - **🟠 Orange:** Stressed vegetation (NDVI 0.0-0.1)
            - **❤️ Red/Dark:** Bare soil/degredation (NDVI < 0.0)
            """)
    
    with tab2:
        st.markdown("**True Color Satellite Imagery**")
        if results['true_color_image'] is not None:
            st.image(results['true_color_image'], use_column_width=True, 
                    caption="**Recent Satellite Observation** - Source: Planet Labs")
            st.info("This true-color image shows the actual appearance of your selected area from space.")
    
    # Export Section
# Export Section
st.markdown("""
<div class="section-header">
    <h2>📤 Export Your Results</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Download your comprehensive land health report for:**
- Professional documentation
- Regulatory compliance
- Project planning
- Progress monitoring
""")

# The create_report_csv function returns the data directly.
# We assign it to a variable and pass it straight to the download button.
csv_data = utils.create_report_csv(st.session_state.aoi, degradation, ndvi_threshold)

st.download_button(
   label="📥 Download Professional Report (CSV)",
   data=csv_data, # Pass the data directly here
   file_name=f"TerraScan_Report_{time.strftime('%Y%m%d_%H%M')}.csv",
   mime="text/csv",
   use_container_width=True,
   help="Includes all analysis data, coordinates, and recommendations"
)

else:
    # Welcome state - no results yet
    st.markdown("""
    <div class="section-header">
        <h2>🚀 Ready to Begin Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Follow these steps to get started:**
    
    1. **🗺️ Draw Your Area** - Use the map above to select your region of interest
    2. **📊 Set Sensitivity** - Adjust the NDVI threshold based on your needs  
    3. **🔍 Start Analysis** - Click the green button to begin satellite processing
    4. **📋 Review Results** - Get detailed health assessment and recommendations
    
    **💡 Pro Tip:** For agricultural areas, start with NDVI 0.2. For natural vegetation, try 0.15.
    """)

# --- PROFESSIONAL FOOTER ---
st.markdown("""
<div class="custom-footer">
    <div class="footer-text">
        <h4>🛰️ TerraScan Professional</h4>
        <p><strong>Advanced Land Health Monitoring Platform</strong></p>
        <p style='font-size: 0.9em; color: #CCCCCC;'>
            Powered by Planet Satellite Imagery 🌍 | Built with Streamlit ⚡
        </p>
    </div>
</div>
""", unsafe_allow_html=True)