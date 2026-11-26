"""StormWatch PH — Maritime & Meteorological Disaster Monitoring Center."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import html as html_lib

import altair as alt
import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & PHILIPPINE RADAR THEME
# -----------------------------------------------------------------------------
PH_LAT_MIN, PH_LAT_MAX = 4.0, 22.0
PH_LON_MIN, PH_LON_MAX = 114.0, 128.0
PHT_TZ = timezone(timedelta(hours=8))

CITIES = {
    "Manila": {"lat": 14.5995, "lon": 120.9842},
    "Cebu City": {"lat": 10.3157, "lon": 123.8854},
    "Davao City": {"lat": 7.1907, "lon": 125.4553},
    "Baguio": {"lat": 16.4023, "lon": 120.5960},
    "Tacloban": {"lat": 11.2433, "lon": 125.0047},
    "Puerto Princesa": {"lat": 9.7392, "lon": 118.7833},
}

USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
TECTONIC_PLATES_URL = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"


def _apply_theme() -> None:
    st.set_page_config(
        page_title="StormWatch PH | Meteorological & Seismic Ops",
        page_icon="🌊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
    """
<style>
    .stApp {
        background-color: #06101b;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background-color: #091727;
        border-right: 1px solid #16324f;
    }
    div[data-testid="metric-container"] {
        background-color: #0d1d30;
        border: 1px solid #16324f;
        border-left: 4px solid #14b8a6;
        padding: 12px 16px;
        border-radius: 6px;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc;
        font-weight: 700;
    }
    .alert-card {
        background-color: #0e1e32;
        border-left: 4px solid #14b8a6;
        padding: 10px 12px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.88rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. METEOROLOGICAL & GEOSPATIAL HELPERS
# -----------------------------------------------------------------------------
def get_wind_direction(degrees: float) -> str:
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees + 22.5) / 45) % 8
    return directions[idx]


def classify_heat_index(temp_c: float) -> str:
    """PAGASA-aligned Heat Index classification bands."""
    if temp_c >= 52:
        return "Extreme Danger"
    if temp_c >= 42:
        return "Danger"
    if temp_c >= 33:
        return "Extreme Caution"
    if temp_c >= 27:
        return "Caution"
    return "Normal"


@st.cache_data(ttl=300)
def fetch_earthquake_data() -> tuple[pd.DataFrame, bool]:
    """Fetch 24h USGS earthquakes filtered to the Philippine Area of Responsibility."""
    try:
        response = requests.get(USGS_API_URL, timeout=8)
        response.raise_for_status()
        data = response.json()

        parsed = []
        for item in data.get("features", []):
            lon, lat, depth = item["geometry"]["coordinates"]
            mag = float(item["properties"].get("mag") or 0)
            if (PH_LAT_MIN <= lat <= PH_LAT_MAX) and (PH_LON_MIN <= lon <= PH_LON_MAX):
                utc_dt = datetime.fromtimestamp(item["properties"]["time"] / 1000, tz=timezone.utc)
                pht_dt = utc_dt.astimezone(PHT_TZ)
                parsed.append(
                    {
                        "place": item["properties"]["place"],
                        "magnitude": round(mag, 2),
                        "time": pht_dt,
                        "lat": lat,
                        "lon": lon,
                        "depth_km": round(float(depth), 1),
                        "severity": "CRITICAL" if mag >= 5.0 else "ADVISORY" if mag >= 4.0 else "NORMAL",
                    }
                )
        df = pd.DataFrame(parsed)
        if not df.empty:
            df = df.sort_values(by="time", ascending=False)
        return df, True
    except Exception:
        # Offline fallback sample telemetry so visualization stays operational
        now_pht = datetime.now(PHT_TZ)
        sample = pd.DataFrame(
            [
                {
                    "place": "42 km E of Surigao City (Cached Sample)",
                    "magnitude": 4.3,
                    "time": now_pht - timedelta(hours=2),
                    "lat": 9.78,
                    "lon": 125.88,
                    "depth_km": 18.0,
                    "severity": "ADVISORY",
                },
                {
                    "place": "18 km SW of Batangas (Cached Sample)",
                    "magnitude": 3.1,
                    "time": now_pht - timedelta(hours=5),
                    "lat": 13.65,
                    "lon": 120.92,
                    "depth_km": 12.0,
                    "severity": "NORMAL",
                },
            ]
        )
        return sample, False


@st.cache_data(ttl=900)
def fetch_weather_data() -> tuple[pd.DataFrame, bool]:
    """Fetch aligned current city telemetry concurrently from Open-Meteo."""
    def _fetch_city(item: tuple[str, dict]) -> dict | None:
        city, coords = item
        try:
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m",
                "timezone": "Asia/Manila",
            }
            resp = requests.get(OPEN_METEO_URL, params=params, timeout=3)
            resp.raise_for_status()
            cur = resp.json().get("current", {})
            feels_like = float(cur.get("apparent_temperature") or 0)
            return {
                "city": city,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "temp": float(cur.get("temperature_2m") or 0),
                "feels_like": feels_like,
                "heat_risk": classify_heat_index(feels_like),
                "humidity": float(cur.get("relative_humidity_2m") or 0),
                "pressure": float(cur.get("surface_pressure") or 0),
                "wind_speed": float(cur.get("wind_speed_10m") or 0),
                "wind_dir": get_wind_direction(float(cur.get("wind_direction_10m") or 0)),
            }
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=len(CITIES)) as pool:
        results = list(pool.map(_fetch_city, CITIES.items()))

    rows = [r for r in results if r is not None]
    live_ok = len(rows) == len(CITIES)

    if not live_ok or not rows:
        fallback = [
            {"city": "Manila", "lat": 14.5995, "lon": 120.9842, "temp": 30.2, "feels_like": 34.5, "heat_risk": "Extreme Caution", "humidity": 72, "pressure": 1009, "wind_speed": 14.0, "wind_dir": "NE"},
            {"city": "Cebu City", "lat": 10.3157, "lon": 123.8854, "temp": 29.4, "feels_like": 33.1, "heat_risk": "Extreme Caution", "humidity": 76, "pressure": 1010, "wind_speed": 16.5, "wind_dir": "E"},
            {"city": "Davao City", "lat": 7.1907, "lon": 125.4553, "temp": 28.8, "feels_like": 32.0, "heat_risk": "Caution", "humidity": 79, "pressure": 1010, "wind_speed": 11.2, "wind_dir": "SE"},
            {"city": "Baguio", "lat": 16.4023, "lon": 120.5960, "temp": 20.1, "feels_like": 20.8, "heat_risk": "Normal", "humidity": 82, "pressure": 1013, "wind_speed": 9.4, "wind_dir": "N"},
            {"city": "Tacloban", "lat": 11.2433, "lon": 125.0047, "temp": 28.5, "feels_like": 32.4, "heat_risk": "Caution", "humidity": 81, "pressure": 1009, "wind_speed": 18.0, "wind_dir": "NE"},
            {"city": "Puerto Princesa", "lat": 9.7392, "lon": 118.7833, "temp": 29.9, "feels_like": 33.8, "heat_risk": "Extreme Caution", "humidity": 74, "pressure": 1010, "wind_speed": 13.0, "wind_dir": "ENE"[:2]},
        ]
        return pd.DataFrame(fallback), False

    return pd.DataFrame(rows), True


@st.cache_data(ttl=86400)
def fetch_tectonic_geojson() -> dict | None:
    try:
        resp = requests.get(TECTONIC_PLATES_URL, timeout=6)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def create_map(quake_df: pd.DataFrame, weather_df: pd.DataFrame) -> folium.Map:
    m = folium.Map(
        location=[12.3, 122.0],
        zoom_start=6,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Dark Gray Canvas",
        control_scale=True,
    )

    plates = fetch_tectonic_geojson()
    if plates:
        folium.GeoJson(
            plates,
            name="Tectonic Plate Boundaries",
            style_function=lambda _: {"color": "#f97316", "weight": 1.2, "opacity": 0.45},
        ).add_to(m)

    if not quake_df.empty:
        for _, row in quake_df.iterrows():
            color = "#14b8a6"
            if row["magnitude"] >= 4.0:
                color = "#f59e0b"
            if row["magnitude"] >= 5.0:
                color = "#ef4444"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=max(row["magnitude"] * 3.0, 5),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"M {row['magnitude']} | {row['place']} ({row['depth_km']} km)",
            ).add_to(m)

    if not weather_df.empty:
        for _, row in weather_df.iterrows():
            html = (
                "<div style='background:rgba(6,16,27,0.88);border:1px solid #14b8a6;"
                "color:#99f6e4;padding:3px 6px;border-radius:4px;font-size:10px;"
                "white-space:nowrap;font-family:sans-serif;'>"
                f"<strong>{row['city']}</strong><br><span style='color:#fff'>{row['temp']:.1f}°C</span></div>"
            )
            tooltip = (
                f"<b>{row['city']}</b><br>"
                f"Temp: {row['temp']:.1f}°C (Feels {row['feels_like']:.1f}°C · {row['heat_risk']})<br>"
                f"Wind: {row['wind_speed']:.1f} km/h {row['wind_dir']} · Humidity: {row['humidity']}%"
            )
            folium.Marker(
                location=[row["lat"], row["lon"]],
                icon=folium.DivIcon(html=html),
                tooltip=tooltip,
            ).add_to(m)

    return m


def filter_weather_by_risk(weather_df: pd.DataFrame, tiers: list[str] | None) -> pd.DataFrame:
    """Filter city meteorological matrix by selected PAGASA heat-index risk tiers."""
    if weather_df.empty or not tiers:
        return weather_df
    return weather_df[weather_df["heat_risk"].isin(tiers)]


def build_hazard_snapshot_html(quake_df: pd.DataFrame, weather_df: pd.DataFrame) -> str:
    """Render an offline printable regional seismic & weather hazard advisory snapshot."""
    q_rows = ""
    if not quake_df.empty:
        q_rows = "".join(
            f"<tr><td>M {float(r['magnitude']):.1f}</td><td>{html_lib.escape(str(r['place']))}</td><td>{float(r['depth_km']):.1f} km</td></tr>"
            for _, r in quake_df.head(10).iterrows()
        )
    else:
        q_rows = "<tr><td colspan='3'>No seismic events above active threshold.</td></tr>"

    w_rows = ""
    if not weather_df.empty:
        w_rows = "".join(
            f"<tr><td>{html_lib.escape(str(r['city']))}</td><td>{float(r['temp']):.1f}°C</td><td>{float(r['feels_like']):.1f}°C</td><td>{html_lib.escape(str(r['heat_risk']))}</td></tr>"
            for _, r in weather_df.iterrows()
        )

    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8' /><title>StormWatch PH Advisory</title></head>"
        "<body style='font-family:system-ui,sans-serif;background:#06101b;color:#f8fafc;padding:2rem;'>"
        "<h1>StormWatch PH — Regional Hazard Advisory Snapshot</h1>"
        "<p>Hotlines: NDRRMC (02) 8911-5061 · Red Cross 143 · Coast Guard (02) 8527-8481</p>"
        "<h2>Seismic Summary</h2><table border='1' cellpadding='6' cellspacing='0'><thead><tr><th>Mag</th><th>Location</th><th>Depth</th></tr></thead>"
        f"<tbody>{q_rows}</tbody></table>"
        "<h2>City Heat Index Status</h2><table border='1' cellpadding='6' cellspacing='0'><thead><tr><th>City</th><th>Temp</th><th>Feels Like</th><th>Tier</th></tr></thead>"
        f"<tbody>{w_rows}</tbody></table></body></html>"
    )


# -----------------------------------------------------------------------------
# 3. MAIN APPLICATION
# -----------------------------------------------------------------------------
def main() -> None:
    _apply_theme()
    quake_df, quake_live = fetch_earthquake_data()
    weather_df, weather_live = fetch_weather_data()

    with st.sidebar:
        st.title("🌊 Radar Controls")
        if st.button("Refresh Live Feeds", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        min_mag = st.slider("Min Seismic Magnitude", 0.0, 7.0, 1.0, 0.5)
        risk_options = ["Normal", "Caution", "Extreme Caution", "Danger", "Extreme Danger"]
        selected_tiers = st.multiselect("Heat-Index Tiers", risk_options, default=risk_options)

        filtered_df = (
            quake_df[quake_df["magnitude"] >= min_mag] if not quake_df.empty else pd.DataFrame()
        )
        filtered_weather = filter_weather_by_risk(weather_df, selected_tiers)

        st.divider()
        st.subheader("Recent Seismic Feed")
        if not filtered_df.empty:
            for _, row in filtered_df.head(5).iterrows():
                accent = "#ef4444" if row["magnitude"] >= 5.0 else "#f59e0b" if row["magnitude"] >= 4.0 else "#14b8a6"
                st.markdown(
                    f"""
                    <div class="alert-card" style="border-left-color:{accent};">
                        <strong style="color:{accent};">M {row['magnitude']}</strong> · {row['place']}<br>
                        <small style="color:#94a3b8;">{row['time'].strftime('%I:%M %p PHT')} | Depth {row['depth_km']} km</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No seismic events above threshold.")

        st.divider()
        st.markdown(
            "**PH Emergency Hotlines**<br>"
            "<span style='color:#cbd5e1;font-size:0.88rem;'>"
            "NDRRMC: <b>(02) 8911-5061</b><br>"
            "Red Cross: <b>143</b><br>"
            "Coast Guard: <b>(02) 8527-8481</b>"
            "</span>",
            unsafe_allow_html=True,
        )

    col_h, col_t = st.columns([3, 1])
    with col_h:
        st.title("StormWatch PH — Ops Center")
        status_note = "Live USGS & Open-Meteo Feeds" if (quake_live and weather_live) else "Fallback Telemetry Mode"
        st.caption(f"Philippine Area of Responsibility · {status_note}")
    with col_t:
        st.markdown(
            f"<div style='text-align:right;font-family:monospace;color:#14b8a6;'>"
            f"PHT TIME<br><span style='font-size:1.4rem;color:#f8fafc;'>"
            f"{datetime.now(PHT_TZ).strftime('%H:%M:%S')}</span></div>",
            unsafe_allow_html=True,
        )

    m1, m2, m3, m4 = st.columns(4)
    quake_count = len(filtered_df)
    max_mag = float(filtered_df["magnitude"].max()) if not filtered_df.empty else 0.0
    avg_temp = float(weather_df["temp"].mean()) if not weather_df.empty else 0.0

    hottest_city, max_heat, risk_tier = "N/A", 0.0, "Normal"
    if not weather_df.empty:
        top_row = weather_df.loc[weather_df["feels_like"].idxmax()]
        hottest_city = top_row["city"]
        max_heat = float(top_row["feels_like"])
        risk_tier = top_row["heat_risk"]

    m1.metric("Detected Quakes (24h)", quake_count)
    m2.metric("Peak Magnitude", f"M {max_mag:.1f}", delta="Alert" if max_mag >= 4.0 else "Normal", delta_color="inverse")
    m3.metric("Mean City Temp", f"{avg_temp:.1f}°C")
    m4.metric(f"Max Heat Index ({hottest_city})", f"{max_heat:.1f}°C", delta=risk_tier)

    tab_map, tab_cities = st.tabs(["Geospatial Radar Map", "City Meteorological Matrix"])
    with tab_map:
        map_obj = create_map(filtered_df, filtered_weather)
        st_folium(map_obj, width="100%", height=440, returned_objects=[])

    with tab_cities:
        if not filtered_weather.empty:
            st.dataframe(
                filtered_weather[["city", "temp", "feels_like", "heat_risk", "humidity", "wind_speed", "wind_dir", "pressure"]],
                use_container_width=True,
                hide_index=True,
            )
            c_csv, c_html = st.columns(2)
            c_csv.download_button(
                "Export City Telemetry CSV",
                data=filtered_weather.to_csv(index=False).encode("utf-8"),
                file_name=f"stormwatch_weather_{datetime.now(PHT_TZ).strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
            c_html.download_button(
                "Download Hazard Advisory (HTML)",
                data=build_hazard_snapshot_html(filtered_df, filtered_weather).encode("utf-8"),
                file_name=f"stormwatch_advisory_{datetime.now(PHT_TZ).strftime('%Y%m%d')}.html",
                mime="text/html",
            )
        else:
            st.info("No cities match the selected heat-index filter.")

    st.subheader("24-Hour Seismic Magnitude Timeline")
    if not filtered_df.empty:
        chart = (
            alt.Chart(filtered_df)
            .mark_bar(width=22, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("time:T", title="Time (PHT)", axis=alt.Axis(format="%H:%M")),
                y=alt.Y("magnitude:Q", title="Magnitude"),
                color=alt.Color("magnitude:Q", scale=alt.Scale(domain=[2, 6.5], range=["#14b8a6", "#f59e0b", "#ef4444"]), legend=None),
                tooltip=["place", "magnitude", "depth_km"],
            )
            .properties(height=220, background="transparent")
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No seismic activity detected in the current filter.")

    st.caption("StormWatch PH · Built by Jann Elijah Limpiado")


if __name__ == "__main__":
    main()
