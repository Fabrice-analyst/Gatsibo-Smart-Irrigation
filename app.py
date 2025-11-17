import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# === LIVE OPEN-METEO API ONLY (NO CSV) ===
@st.cache_data(ttl=3600)
def get_openmeteo_forecast():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': -1.5789, 'longitude': 30.5089,
        'daily': ['temperature_2m_max', 'precipitation_sum', 'et0_fao_evapotranspiration'],
        'timezone': 'Africa/Kigali', 'forecast_days': 7
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame({
            'date': pd.to_datetime(data['daily']['time']),
            'et0_mm': data['daily']['et0_fao_evapotranspiration'],
            'rainfall_mm': data['daily']['precipitation_sum'],
            'temp_max': data['daily']['temperature_2m_max']
        })
        df['irrigation_mm'] = (df['et0_mm'] * 0.8) - df['rainfall_mm']
        df['irrigation_mm'] = df['irrigation_mm'].clip(lower=0).round(1)
        st.success("Live Forecast from Open-Meteo API (FAO-56 ET₀)")
        return df
    except Exception as e:
        st.error(f"API failed: {e}. Using demo data.")
        # Fallback demo data (no file needed)
        return pd.DataFrame({
            'date': pd.date_range(start='2025-11-17', periods=7),
            'temp_max': [28.5, 29.1, 27.8, 30.2, 28.9, 29.5, 28.0],
            'rainfall_mm': [0.0, 2.1, 5.3, 0.0, 1.2, 0.0, 3.4],
            'et0_mm': [4.2, 4.5, 4.0, 4.8, 4.3, 4.6, 4.1],
            'irrigation_mm': [3.4, 1.5, 0.0, 3.8, 2.2, 3.7, 0.0]
        })

# === LOAD FORECAST ===
forecast_7day = get_openmeteo_forecast()

# === UI (YOUR ORIGINAL STYLE) ===
st.title("Gatsibo Smart Irrigation Scheduler")
st.markdown("### Live 7-Day Irrigation Forecast (Real-Time ET₀ & Rainfall)")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("7-Day Forecast")
    display = forecast_7day[['date', 'temp_max', 'rainfall_mm', 'et0_mm', 'irrigation_mm']].copy()
    display['date'] = display['date'].dt.strftime('%b %d')
    display = display.round(1)
    st.dataframe(display.style.highlight_min(axis=0, subset=['irrigation_mm'], color='#ffcccc'))

with col2:
    st.subheader("Summary")
    total_irrigation = forecast_7day['irrigation_mm'].sum().round(1)
    total_rain = forecast_7day['rainfall_mm'].sum().round(1)
    st.metric("Total Irrigation Needed", f"{total_irrigation} mm")
    st.metric("Total Rainfall", f"{total_rain} mm")
    st.metric("Water Saved", f"{(total_rain * 0.8):.1f} mm")

st.subheader("Irrigation vs Rainfall")
fig = px.bar(forecast_7day, x='date', y=['irrigation_mm', 'rainfall_mm'],
             barmode='group', color_discrete_map={'irrigation_mm': '#ff6b6b', 'rainfall_mm': '#4ecdc4'})
fig.update_xaxes(tickformat='%b %d')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("**Fabrice Rutagarama** | [GitHub](https://github.com/Fabrice-analyst) | [Live App](https://gatsibo-smart-irrigation.streamlit.app)")
st.caption("Data: Open-Meteo API (FAO-56) | Auto-updates hourly | No CSV. No notebook.")
