import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Step 1: Load the bird flu data
df = pd.read_csv('birdflu.csv')

# Step 2: Load the county centroids data
# This file should have columns: 'State', 'County', 'Latitude', 'Longitude'
centroids = pd.read_csv('county_centroids.csv')

# After loading both datasets, before merging:
print("Sample from bird flu data:")

# Step 4: Check for missing centroids
print(centroids[['State', 'County']].head())

# Clean up county names
df['County'] = df['County'].str.replace(' County', '').str.strip()
centroids['County'] = centroids['County'].str.replace(' County', '').str.strip()

# Convert state names to standard format
def standardize_state_name(state):
    # Dictionary of state name mappings (full name to abbreviation)
    state_dict = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
        'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
        'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    return state_dict.get(state, state)

# Standardize state names in both dataframes
df['State'] = df['State'].apply(standardize_state_name)
centroids['State'] = centroids['State'].apply(standardize_state_name)

# Step 3: Merge the DataFrames to add latitude and longitude
df_merged = pd.merge(df, centroids, on=['State', 'County'], how='left')

# Step 4: Check for missing centroids
missing = df_merged[df_merged['Latitude'].isna()]
if not missing.empty:
    print("Missing centroids for the following counties:")
    print(missing[['State', 'County']].drop_duplicates())

# Check missing matches after cleaning
missing = df_merged[df_merged['Latitude'].isna()]
if not missing.empty:
    print("\nMissing centroids after cleaning:")
    missing_counts = missing[['State', 'County']].drop_duplicates()
    print(f"Total missing counties: {len(missing_counts)}")
    print("\nSample of missing counties:")
    print(missing_counts.head(10))

    # Step 5: Create a Folium map centered on the US
# Location [37.0902, -95.7129] is roughly the US geographic center, zoom_start=4 shows the whole country
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

# Step 6: Add a MarkerCluster layer to handle large number of points
marker_cluster = MarkerCluster().add_to(m)

# Step 7: Add markers for each instance
for index, row in df_merged.iterrows():
    # Skip rows with missing coordinates
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Date: {row['Collection Date']}<br>Species: {row['Bird Species']}<br>Strain: {row['HPAI Strain']}",
            icon=folium.Icon(color='red')
        ).add_to(marker_cluster)

# Display the map directly in the notebook
display(m)