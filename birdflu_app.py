import streamlit as st
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
import numpy as np
from streamlit_folium import st_folium
from pathlib import Path

# Set page config with caching
st.set_page_config(page_title="Bird Flu Tracker", layout="wide")
st.title("Bird Flu Cases Map")

@st.cache_data
def load_data():
    data_dir = Path(__file__).parent / "data"
    try:
        df = pd.read_csv(data_dir / "birdflu.csv")
        centroids = pd.read_csv(data_dir / "county_centroids.csv")
        return df, centroids
    except FileNotFoundError:
        st.error("Data files not found. Please check the data directory.")
        return None, None

# Load data
df, centroids = load_data()

if df is not None and centroids is not None:
    # Clean and merge data more efficiently
    df['County'] = df['County'].str.replace(' County', '').str.strip()
    centroids['County'] = centroids['County'].str.replace(' County', '').str.strip()

    @st.cache_data
    def standardize_state_name(state):
        state_dict = {
            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
            # ...existing state mappings...
        }
        return state_dict.get(state, state)

    # Process data with vectorized operations
    df['State'] = df['State'].map(standardize_state_name)
    centroids['State'] = centroids['State'].map(standardize_state_name)
    
    # Merge data more efficiently
    df_merged = pd.merge(df, centroids[['State', 'County', 'Latitude', 'Longitude']], 
                        on=['State', 'County'], 
                        how='left')

    # Create base map
    m = folium.Map(location=[37.0902, -95.7129], 
                   zoom_start=4,
                   prefer_canvas=True)  # Use canvas renderer for better performance

    # Prepare data for FastMarkerCluster
    @st.cache_data
    def prepare_cluster_data(df):
        valid_points = df[df['Latitude'].notna() & df['Longitude'].notna()]
        return (valid_points[['Latitude', 'Longitude']]
                .to_numpy()
                .tolist())

    points = prepare_cluster_data(df_merged)

    # Use FastMarkerCluster instead of MarkerCluster
    FastMarkerCluster(
        data=points,
        options={
            'maxClusterRadius': 30,
            'disableClusteringAtZoom': 8
        }
    ).add_to(m)

    # Add a choropleth layer for state-level summary if needed
    @st.cache_data
    def get_state_summary(df):
        return df.groupby('State').size().reset_index(name='count')

    state_summary = get_state_summary(df_merged)

    # Display map with minimal state updates
    st_data = st_folium(
        m,
        width=1200,
        height=600,
        returned_objects=[],  # Minimize state updates
        key="bird_flu_map"
    )

    # Show statistics using cached calculations
    @st.cache_data
    def calculate_stats(df):
        return {
            'total_cases': len(df),
            'states_affected': df['State'].nunique(),
            'counties_affected': df['County'].nunique()
        }
    
    stats = calculate_stats(df_merged)
    
    # Display metrics in columns
    cols = st.columns(3)
    for col, (label, value) in zip(cols, stats.items()):
        col.metric(label.replace('_', ' ').title(), value)

    # Handle missing data efficiently
    missing_count = df_merged['Latitude'].isna().sum()
    if missing_count > 0:
        with st.expander(f"Missing coordinates for {missing_count} cases"):
            st.dataframe(
                df_merged[df_merged['Latitude'].isna()][['State', 'County']]
                .drop_duplicates()
                .sort_values(['State', 'County'])
            )
