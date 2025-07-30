# Quick Interactive Maps Generation
# Run this after the main notebook to create maps

import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import json

# Load the results
df = pd.read_csv('results/jet_fuel_opportunities.csv')
print(f"Loaded {len(df)} scored airports")

# ========================================
# MAP 1: OPPORTUNITY HEAT MAP
# ========================================

print("\nCreating heat map...")

# Create base map
m1 = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Prepare heat map data
heat_data = []
for idx, row in df.iterrows():
    if pd.notna(row['LAT_DECIMAL']) and pd.notna(row['LONG_DECIMAL']):
        heat_data.append([row['LAT_DECIMAL'], row['LONG_DECIMAL'], row['predicted_score']])

# Add heat map
HeatMap(heat_data, 
        min_opacity=0.3,
        radius=15,
        blur=15,
        gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'orange', 1: 'red'}).add_to(m1)

# Add title
title_html = '''
<h3 align="center" style="font-size:20px"><b>Jet Fuel Infrastructure Opportunity Heat Map</b></h3>
<p align="center">Red = Highest Opportunity | Blue = Lower Opportunity</p>
'''
m1.get_root().html.add_child(folium.Element(title_html))

# Save
m1.save('opportunity_heatmap.html')
print("✓ Saved: opportunity_heatmap.html")

# ========================================
# MAP 2: TOP OPPORTUNITIES WITH DETAILS
# ========================================

print("\nCreating detailed opportunities map...")

# Create base map
m2 = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Add marker cluster
marker_cluster = MarkerCluster().add_to(m2)

# Add top opportunities (score > 70)
high_opportunities = df[df['predicted_score'] >= 70].copy()

for idx, row in high_opportunities.iterrows():
    if pd.notna(row['LAT_DECIMAL']) and pd.notna(row['LONG_DECIMAL']):
        # Determine marker color
        if row['predicted_score'] >= 85:
            color = 'red'
            icon = 'star'
        elif row['predicted_score'] >= 75:
            color = 'orange'
            icon = 'plane'
        else:
            color = 'yellow'
            icon = 'info-sign'
        
        # Create popup
        popup_text = f"""
        <b>{row['ARPT_NAME']}</b><br>
        City: {row['CITY']}, {row['STATE_NAME']}<br>
        Opportunity Score: {row['predicted_score']:.1f}<br>
        Certification Level: {row['cert_importance_score']}<br>
        Military Relevant: {'Yes' if row['is_military_relevant'] else 'No'}
        """
        
        # Add marker
        folium.Marker(
            location=[row['LAT_DECIMAL'], row['LONG_DECIMAL']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=color, icon=icon),
            tooltip=f"{row['ARPT_NAME']} - Score: {row['predicted_score']:.1f}"
        ).add_to(marker_cluster)

# Add legend
legend_html = '''
<div style="position: fixed; 
            top: 10px; right: 10px; width: 200px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius: 5px; padding: 10px">
    <p style="margin: 0;"><b>Opportunity Score Legend</b></p>
    <p style="margin: 5px;"><i class="fa fa-star" style="color:red"></i> Critical (85+)</p>
    <p style="margin: 5px;"><i class="fa fa-plane" style="color:orange"></i> High (75-85)</p>
    <p style="margin: 5px;"><i class="fa fa-info-circle" style="color:yellow"></i> Medium (70-75)</p>
</div>
'''
m2.get_root().html.add_child(folium.Element(legend_html))

# Save
m2.save('detailed_opportunities.html')
print(f"✓ Saved: detailed_opportunities.html ({len(high_opportunities)} airports shown)")

# ========================================
# MAP 3: STATE-LEVEL SUMMARY
# ========================================

print("\nCreating state summary map...")

# Calculate state summaries
state_summary = df.groupby('STATE_NAME').agg({
    'predicted_score': ['mean', 'max', 'count']
}).round(2)
state_summary.columns = ['avg_score', 'max_score', 'count']

# Create base map
m3 = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Simple state centers (abbreviated list for speed)
state_centers = {
    'Texas': [31.054487, -97.563461],
    'California': [36.116203, -119.681564],
    'Florida': [27.766279, -81.686783],
    'Alaska': [61.370716, -152.404419],
    'Montana': [46.921925, -110.454353],
    'New York': [42.165726, -74.948051],
    'Arizona': [33.729759, -111.431221],
    'Nevada': [38.313515, -117.055374],
    'Colorado': [39.059811, -105.311104],
    'Illinois': [40.349457, -88.986137],
    'Georgia': [33.040619, -83.643074],
    'Michigan': [43.326618, -84.536095],
    'Pennsylvania': [40.590752, -77.209755],
    'Ohio': [40.388783, -82.764915],
    'North Carolina': [35.630066, -79.806419]
}

# Add circles for each state
for state, stats in state_summary.iterrows():
    if state in state_centers:
        # Color based on average score
        if stats['avg_score'] >= 60:
            color = 'red'
        elif stats['avg_score'] >= 50:
            color = 'orange'
        elif stats['avg_score'] >= 40:
            color = 'yellow'
        else:
            color = 'green'
        
        # Popup text
        popup_text = f"""
        <b>{state}</b><br>
        Avg Score: {stats['avg_score']:.1f}<br>
        Max Score: {stats['max_score']:.1f}<br>
        Opportunities: {int(stats['count'])}
        """
        
        # Add circle
        folium.CircleMarker(
            location=state_centers[state],
            radius=min(stats['count'] / 10, 30),
            popup=folium.Popup(popup_text, max_width=200),
            color='black',
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m3)

# Add title
title_html = '''
<h3 align="center" style="font-size:20px"><b>State-Level Investment Opportunities</b></h3>
<p align="center">Circle size = Number of opportunities | Color = Average score</p>
'''
m3.get_root().html.add_child(folium.Element(title_html))

# Save
m3.save('state_opportunities.html')
print("✓ Saved: state_opportunities.html")

print("\n✓ All maps created successfully!")
print("\nMap files generated:")
print("1. opportunity_heatmap.html - Heat map of all opportunities")
print("2. detailed_opportunities.html - Interactive markers for high-score airports")
print("3. state_opportunities.html - State-level summary view")