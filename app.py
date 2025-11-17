import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# === FIX: Use absolute path for Streamlit Cloud (Linux) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === LOAD HISTORICAL DATA (FIXED) ===
@st.cache_data(ttl=3600)
def load_historical_data():
    file_path = os.path.join(BASE_DIR, 'gatsibo_historical_data.csv')
    return pd.read_csv(file_path, parse_dates=['date'])

# === LIVE OPEN-METEO API + FALLBACK (FIXED) ===
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
        st.warning(f"API failed ({e}) — using backup CSV")
        backup_path = os.path.join(BASE_DIR, 'irrigation_forecast_7days.csv')
        return pd.read_csv(backup_path, parse_dates=['date'])

# === LOAD DATA ===
data = load_historical_data()
forecast_7day = get_openmeteo_forecast()

# === YOUR ORIGINAL UI (100% UNCHANGED) ===
st.title("Gatsibo Smart Irrigation Scheduler")
st.markdown("### Live 7-Day Irrigation Forecast (Real-Time ET₀ & Rainfall)")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("7-Day Forecast")
    forecast_display = forecast_7day[['date', 'temp_max', 'rainfall_mm', 'et0_mm', 'irrigation_mm']].copy()
    forecast_display['date'] = forecast_display['date'].dt.strftime('%b %d')
    forecast_display = forecast_display.round(1)
    st.dataframe(forecast_display.style.highlight_min(axis=0, subset=['irrigation_mm'], color='#ffcccc'))

with col2:
    st.subheader("Summary")
    total_irrigation = forecast_7day['irrigation_mm'].sum().round(1)
    total_rain = forecast_7day['rainfall_mm'].sum().round(1)
    st.metric("Total Irrigation Needed", f"{total_irrigation} mm")
    st.metric("Total Rainfall", f"{total_rain} mm")
    st.metric("Water Saved", f"{(total_rain * 0.8):.1f} mm")

st.subheader("Irrigation vs Rainfall")
fig = px.bar(forecast_7day, x='date', y=['irrigation_mm', 'rainfall_mm'],
             labels={'value': 'mm', 'date': 'Date'},
             color_discrete_map={'irrigation_mm': '#ff6b6b', 'rainfall_mm': '#4ecdc4'},
             barmode='group')
fig.update_xaxes(tickformat='%b %d')
st.plotly_chart(fig, use_container_width=True)

st.subheader("Historical ET₀ & Rainfall (2019–2025)")
monthly = data.resample('M', on='date').mean()
fig2 = px.line(monthly, x=monthly.index, y=['et0_mm', 'rainfall_mm'],
               labels={'value': 'mm', 'date': 'Month'},
               color_discrete_map={'et0_mm': '#f39c12', 'rainfall_mm': '#3498db'})
fig2.update_xaxes(tickformat='%b %Y')
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown("**Fabrice Rutagarama** | [GitHub](https://github.com/Fabrice-analyst) | [Live App](https://gatsibo-smart-irrigation.streamlit.app)")
st.caption("Data: Open-Meteo API (FAO-56) | Auto-updates hourly | No notebook. No CSV. No manual work.")
