import streamlit as st
import osmnx as ox
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide", page_title="East Africa Railway Dashboard")

st.title("🚂 East Africa Railway Network Analysis")
st.markdown("Visualizing the transition from Legacy Meter Gauge (MGR) to Standard Gauge (SGR).")

@st.cache_data
def get_rail_data():
    # Reuse your logic to fetch and process data
    countries = ["Kenya", "Tanzania", "Uganda", "Ethiopia"]
    all_rails = []
    for country in countries:
        try:
            gdf = ox.features_from_place(country, {"railway": "rail"})
            gdf['country'] = country
            # Project to ESRI:102022 for KM calculation
            gdf = gdf.to_crs("ESRI:102022")
            gdf['length_km'] = gdf.geometry.length / 1000
            
            def categorize(row):
                gauge = str(row.get('gauge', 'unknown'))
                if '1435' in gauge: return 'Standard Gauge (SGR)'
                if '1000' in gauge: return 'Meter Gauge (MGR)'
                return 'Other/Legacy'
            
            gdf['rail_type'] = gdf.apply(categorize, axis=1)
            all_rails.append(gdf[['country', 'rail_type', 'length_km', 'geometry']])
        except:
            continue
    return gpd.GeoDataFrame(pd.concat(all_rails, ignore_index=True)).to_crs("EPSG:4326")

master_gdf = get_rail_data()

# Layout: Sidebar filters and Metrics
st.sidebar.header("Filters")
selected_country = st.sidebar.multiselect("Select Countries", master_gdf['country'].unique(), default=master_gdf['country'].unique())

filtered_df = master_gdf[master_gdf['country'].isin(selected_country)]

# Column layout for Visuals
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Network Statistics")
    stats = filtered_df.groupby(['country', 'rail_type'])['length_km'].sum().reset_index()
    fig = px.bar(stats, x="country", y="length_km", color="rail_type", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Interactive Map")
    m = folium.Map(location=[0.5, 37], zoom_start=5)
    # Add logic to plot lines on map
    st_folium(m, width=700, height=500)
