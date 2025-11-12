"""
GATSIBO SMART IRRIGATION SCHEDULER - FINAL & COMPLETE
Author: Fabrice RUTAGARAMA
Date: November 12, 2025
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Gatsibo Smart Irrigation",
    page_icon="drop",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CSS (includes fixed footer)
# ============================================================================
st.markdown(
    """
<style>
    /* Main background */
    .stApp, .main, [data-testid="stAppViewContainer"] {background-color: #0E1117 !important; color: #E0E0E0 !important;}
    section[data-testid="stSidebar"] {background-color: #0E1117 !important;}

    /* Text */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label, .stMarkdown {color: #E0E0E0 !important;}
    .stMarkdown a {color: #64B5F6 !important;}

    /* Sidebar */
    .sidebar h3 {color: #64B5F6 !important; font-weight: bold; margin: 1rem 0 0.5rem 0;}

    /* Radio buttons */
    .stRadio > div > label > div:first-child {background-color: #1E2130 !important; border: 1px solid #444 !important;}
    .stRadio > div > label > div:last-child {color: #E0E0E0 !important;}

    /* Metrics */
    .stMetric {background-color: #1E2130 !important; color: white !important; border-radius: 10px; padding: 12px; border: 1px solid #444;}

    /* Alerts */
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {
        background-color: #1E2130 !important; color: #E0E0E0 !important; border-left: 4px solid #64B5F6 !important;
    }

    /* Footer */
    .footer {
        position: fixed;
        left: 0; bottom: 0; width: 100%;
        background-color: #1A1F2E;
        color: #AAAAAA;
        text-align: center;
        padding: 1rem;
        font-size: 0.9rem;
        border-top: 2px solid #64B5F6;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(100, 181, 246, 0.15);
    }
    .block-container, [data-testid="stAppViewContainer"] {padding-bottom: 6rem !important;}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data(ttl=604800)  # 1 week cache
def load_data():
    data = pd.read_csv('gatsibo_complete_irrigation_data.csv', index_col=0, parse_dates=True)
    forecast = pd.read_csv('irrigation_forecast_7days.csv', parse_dates=['date'])
    return data, forecast

data, forecast_7day = load_data()

# ============================================================================
# HEADER
# ============================================================================
st.markdown(
    '<h1 style="text-align: center; color: #64B5F6; font-size: 3rem;">Gatsibo Smart Irrigation Scheduler</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='text-align: center; color: #BBBBBB;'>AI-Powered Weekly Forecast | Auto-Updated Every Sunday</div>",
    unsafe_allow_html=True,
)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/17/Flag_of_Rwanda.svg", width=80)
    st.markdown("<h3>Navigation</h3>", unsafe_allow_html=True)
    page = st.radio(
        "Select Page",
        ["Dashboard", "7-Day Forecast", "Historical", "About Gatsibo", "About This Tool"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("<h3>Quick Stats</h3>", unsafe_allow_html=True)
    st.metric("Days Analyzed", f"{len(data):,}")
    st.metric("Model Accuracy", "82% (R² = 0.82)")
    st.metric("Last Updated", datetime.now().strftime("%b %d, %Y"))

# ============================================================================
# PAGES
# ============================================================================
if page == "Dashboard":
    st.markdown('<h2 style="color: #66BB6A; margin-top: 2rem;">This Week\'s Irrigation Forecast</h2>', unsafe_allow_html=True)
    today = datetime.now().date()
    week_ending = today + timedelta(days=(6 - today.weekday()) % 7)
    if week_ending <= today:
        week_ending += timedelta(days=7)

    st.success(f"AI Forecast for **{today.strftime('%b %d')} – {week_ending.strftime('%b %d, %Y')}** (R² = 0.82)")

    total = forecast_7day['irrigation_mm'].sum()
    daily = total / 7
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Week Ending", week_ending.strftime("%b %d"))
    with col2: st.metric("Total Needed", f"{total:.1f} mm")
    with col3: st.metric("Daily Avg", f"{daily:.1f} mm")

    # Irrigation level
    if total < 5:
        rec, color, label = "MINIMAL", "#4CAF50", "MINIMAL"
    elif total < 20:
        rec, color, label = "LIGHT", "#FFC107", "LIGHT"
    elif total < 40:
        rec, color, label = "MODERATE", "#FF9800", "MODERATE"
    else:
        rec, color, label = "HEAVY", "#F44336", "HEAVY"

    irrigation_days = forecast_7day[forecast_7day['irrigation_mm'] > 0.5]
    irrigation_days_count = len(irrigation_days)
    split_text = f"split {irrigation_days_count} times" if irrigation_days_count > 0 else "no irrigation needed"

    st.markdown(
        f"<div style='background-color: {color}22; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid {color};'>"
        f"<h3 style='margin: 0; color: {color};'>{label} Irrigation This Week</h3>"
        f"<p><b>Apply:</b> {total:.0f} mm ({split_text})</p></div>",
        unsafe_allow_html=True,
    )

    if not irrigation_days.empty:
        days_list = irrigation_days['date'].dt.strftime('%a').tolist()
        amounts = irrigation_days['irrigation_mm'].round(1).tolist()
        schedule = "<br>".join([f"• <b>{day}</b>: {amt} mm" for day, amt in zip(days_list, amounts)])
        st.markdown(
            f"<div style='background-color: #1E2130; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #64B5F6; margin-top: 1rem;'>"
            f"<h4 style='margin: 0; color: #64B5F6;'>Recommended Irrigation Days</h4>"
            f"<p style='margin: 0.5rem 0; color: #E0E0E0;'>{schedule}</p>"
            f"<p style='font-size: 0.9rem; color: #AAAAAA;'><i>Only irrigate on days with >0.5 mm need. Rain covers the rest.</i></p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No irrigation needed this week — rain is sufficient!")

elif page == "7-Day Forecast":
    st.markdown('<h2 style="color: #66BB6A;">Daily Forecast</h2>', unsafe_allow_html=True)
    forecast_display = forecast_7day.copy()
    forecast_display['date'] = forecast_display['date'].dt.strftime('%a, %b %d')
    st.dataframe(forecast_display, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=forecast_7day['date'].dt.strftime('%b %d'),
            y=forecast_7day['irrigation_mm'],
            marker_color='#66BB6A',
            text=forecast_7day['irrigation_mm'].round(1),
            textposition='outside',
        )
    )
    fig.update_layout(
        title="7-Day Irrigation Forecast",
        xaxis_title="Date",
        yaxis_title="Irrigation (mm)",
        height=450,
        plot_bgcolor='#1E2130',
        paper_bgcolor='#0E1117',
        font_color='#E0E0E0',
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Historical":
    st.markdown('<h2 style="color: #66BB6A;">Historical Trends (2019–2025)</h2>', unsafe_allow_html=True)
    monthly = data['Irrigation_requirement_mm'].resample('ME').mean()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly.index,
            y=monthly.values,
            mode='lines+markers',
            line=dict(color='#64B5F6', width=3),
        )
    )
    fig.update_layout(
        title="Monthly Irrigation Requirement",
        xaxis_title="Year",
        yaxis_title="Irrigation (mm/day)",
        height=500,
        plot_bgcolor='#1E2130',
        paper_bgcolor='#0E1117',
        font_color='#E0E0E0',
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "About Gatsibo":
    st.markdown('<h2 style="color: #66BB6A;">About Gatsibo District</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            """
### Location
- **Province:** Eastern Province, Rwanda  
- **Coordinates:** 1.58°S, 30.51°E  
- **Elevation:** ~1,450 meters  
- **Focus Area:** Gabiro irrigation scheme  

### Agriculture
- **Main Crops:** Maize, rice, vegetables  
- **Irrigation Systems:** Drip, sprinkler, furrow  
- **Climate:** Highland tropical, bimodal rainfall  
- **Rainfall:** 900–1,400 mm/year  

### Water Resources
- **Rivers:** Akagera watershed  
- **Schemes:** Gabiro, Kabarore  
- **Challenges:** Seasonal water stress
"""
        )
    with col2:
        fig = go.Figure(
            go.Scattermapbox(
                lat=[-1.5789],
                lon=[30.5089],
                mode='markers',
                marker=go.scattermapbox.Marker(size=20, color='red'),
                text=['Gabiro Irrigation Scheme'],
                hoverinfo='text',
            )
        )
        fig.update_layout(
            mapbox=dict(style="open-street-map", center=dict(lat=-1.65, lon=30.55), zoom=9),
            height=500,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor='#0E1117',
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Project Impact")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Water Savings**\n\nFor 100 ha:\n- ~21,700 m³/year\n- 20–30% reduction")
    with c2:
        st.success("**Crop Benefits**\n\n- Higher yields\n- Less stress\n- Climate resilience")
    with c3:
        st.warning("**Environment**\n\n- Watershed protection\n- Sustainable farming")

elif page == "About This Tool":
    st.markdown('<h2 style="color: #66BB6A;">About This Tool</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
### Project Overview
The **Gatsibo Smart Irrigation Scheduler** is an AI-powered tool that provides data-driven
irrigation recommendations for farmers in Gatsibo District, Rwanda.

### Technology Stack
- **Satellite Data:** Sentinel-2 imagery (10m resolution)  
- **Weather Data:** NASA POWER API  
- **ET₀ Calculation:** FAO-56 Penman-Monteith  
- **Crop Coefficients:** NDVI-based Kc  
- **Machine Learning:** Random Forest (R² = 0.82)  
- **Web Framework:** Streamlit  

### Data Sources
- **Period:** 2019–2025 (6 years)  
- **Satellite images:** 83 cloud-free scenes  
- **Weather observations:** 2,134 days  

### Methodology
1. **ET₀:** Penman-Monteith using weather data  
2. **Kc:** Derived from NDVI  
3. **ETc:** ET₀ × Kc  
4. **Effective Rainfall:** 80% of total  
5. **Irrigation Need:** ETc - Effective Rainfall  
6. **Forecast:** 7-day AI prediction  

### Model Performance
- **Accuracy:** R² = 0.82  
- **Error:** MAE = 0.54 mm/day  
- **Top Feature:** ET₀ (42.8%)  

---
**Built with dedication for Rwanda's agricultural future**
"""
        )
    with col2:
        st.image("https://i.ibb.co/TM3psZjw/photo-jpg.jpg", width=180)
        st.markdown(
            """
<div style='text-align: center; margin-top: 1rem;'>
    <b style='color: white; font-size: 1.1rem;'>Fabrice RUTAGARAMA</b><br>
    <small style='color: #64B5F6;'><i>BSc Irrigation & Drainage</i></small><br>
    <small style='color: #64B5F6;'><i>MSc Agribusiness (Year 1)</i></small><br>
    <small style='color: #BBBBBB;'><b>University of Rwanda</b></small><br><br>
    <small style='color: #90CAF9; font-weight: bold;'>Certified Data Analyst – ALX Africa</small><br>
    <small style='color: #AAAAAA;'>Agriculture Engineer • Data Analyst • ML Engineer</small>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("### Contact & Feedback")
    st.info(
        """
**Email:** rutagaramafabrice7@gmail.com  
**Phone:** +250 781 587 69  

Have feedback? Want to collaborate? Reach out!
"""
    )

# ============================================================================
# FIXED FOOTER — ALWAYS VISIBLE
# ============================================================================
st.markdown(
    """
<div class="footer">
    <p style="margin: 0; font-size: 0.9rem;">
        <strong>Gatsibo Smart Irrigation Scheduler</strong> • 
        Built with data science for Rwanda’s agricultural resilience.<br>
        <span style="color: #64B5F6;">© 2025 Fabrice RUTAGARAMA</span> • 
        <a href="mailto:rutagaramafabrice7@gmail.com" style="color: #90CAF9; text-decoration: none;">Contact</a>
    </p>
</div>
""",
    unsafe_allow_html=True,
)
