# 🌪️ StormWatch PH

**Real-Time Disaster Monitoring Dashboard**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B)
![Status](https://img.shields.io/badge/Status-Live-success)

## 📖 Overview
**StormWatch PH** is a "Command Center" style dashboard designed to monitor seismic activity and weather conditions in the Philippines in real-time. 

Built with **Python** and **Streamlit**, it aggregates data from global APIs, processes geospatial information using **Pandas**, and visualizes potential risks using **Folium** maps and **Altair** charts. This tool is designed to provide quick situational awareness during natural disasters.

## 🚀 Key Features
*   **Live Earthquake Feed:** Fetches real-time data from the **USGS API**, filtered specifically for the Philippine Area of Responsibility (PAR).
*   **Geospatial Visualization:** Interactive dark-mode map plotting earthquake epicenters (sized by magnitude) and tectonic plate boundaries.
*   **Weather Telemetry:** Real-time temperature, wind, heat index, and humidity tracking for major PH cities via **Open-Meteo API**.
*   **Analytics Engine:** Dynamic bar charts visualizing seismic frequency and magnitude trends over the last 24 hours.
*   **Alert System:** Sidebar feed highlighting critical quakes (Magnitude 4.0+) with visual urgency indicators.

## 🛠️ Tech Stack
*   **Core:** Python 3.x
*   **UI/Framework:** Streamlit
*   **Data Manipulation:** Pandas, NumPy
*   **Geospatial/Map:** Folium, Streamlit-Folium
*   **Visualization:** Altair
*   **APIs:** USGS Earthquake Feed, Open-Meteo, GitHub GeoJSON (Tectonic Plates)

## 📦 Installation & Usage

1.  **Clone the repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/stormwatch-ph.git
    cd stormwatch-ph
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**
    ```bash
    streamlit run app.py
    ```

## 📊 Data Sources
1.  **USGS Earthquake Hazards Program** (Real-time GeoJSON Feed)
2.  **Open-Meteo** (Weather Forecast API)
3.  **Hugo Ahlenius, Nordpil** (Tectonic Plate Boundaries)

## 👤 Author
**Jann Elijah Limpiado**  
*Data Engineer | Python Developer*

---
*This project is for educational and portfolio purposes.*