import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# --- 1. SETUP & LOADING ---
# Ensure your file in the sidebar is named exactly '2025.csv'
file_path = 'encampment_data - 2025.csv'
df = pd.read_csv(file_path)
df = df.dropna(subset=['Location', 'Type'])

# Initialize the Geocoder (The tool that finds coordinates)
geolocator = Nominatim(user_agent="dc_reporter_tool")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# --- 2. DATA CLEANING ---
# We look for keywords in your "Type" column to categorize the markers
df['is_full_cleanup'] = df['Type'].str.contains('Full Clean-up', na=False)
df['is_biohazard'] = df['Type'].str.contains('Bio-hazard', na=False)

# Notice we added an extra .str before .strip()
df['map_address'] = df['Location'].str.split('/').str[0].str.strip() + ", Washington, DC"

# --- 3. GEOCODING (Finding Lat/Long) ---
print("Scanning DC for coordinates... please wait (1 second per row).")
df['point'] = df['map_address'].apply(geocode)
df['lat'] = df['point'].apply(lambda x: x.latitude if x else None)
df['lon'] = df['point'].apply(lambda x: x.longitude if x else None)

# Drop any rows that couldn't be found on the map
df = df.dropna(subset=['lat'])

# --- 4. BUILDING THE MAP ---
# Center the map on Washington, D.C.
m = folium.Map(location=[38.9072, -77.0369], zoom_start=13, tiles="cartodbpositron")

for idx, row in df.iterrows():
    # Logic: Red for Full Clean-up, Orange for Bio-hazard only, Blue for others
    if row['is_full_cleanup']:
        dot_color = 'red'
    elif row['is_biohazard']:
        dot_color = 'orange'
    else:
        dot_color = 'blue'

    # Create the popup content
    popup_text = f"""
    <b>Date:</b> {row['Date']}<br>
    <b>Location:</b> {row['Location']}<br>
    <b>Type:</b> {row['Type']}<br>
    <b>Ward:</b> {row['Ward']}
    """
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=7,
        color=dot_color,
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# --- 5. SAVE THE WEBPAGE ---
# --- 5. CREATE THE FULL WEBPAGE LAYOUT ---

# Define your banner and text
title = "Washington D.C. Encampment Closure Tracker (2025)"
description = """
<p>This interactive map tracks municipal encampment cleanup and enforcement activities across the District. 
Data is categorized by the type of engagement, including full clean-ups, bio-hazard removals, and safety enforcements. 
Click on any marker to see the date, specific location, and associated Ward.</p>
"""

# Generate the map HTML as a string
map_html = m._repr_html_()

# Combine everything into a professional layout
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: 'Helvetica', sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .content {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ margin: 0; font-size: 24px; }}
        p {{ line-height: 1.6; color: #34495e; }}
        .map-container {{ height: 600px; margin-top: 20px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
    </div>
    <div class="content">
        {description}
        <div class="map-container">
            {map_html}
        </div>
    </div>
</body>
</html>
"""

# Save this new, complete webpage
with open('index.html', 'w') as f:
    f.write(full_html)

print("Professional webpage created! Check index.html.")