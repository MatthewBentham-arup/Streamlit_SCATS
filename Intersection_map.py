import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pydeck as pdk
import streamlit as st
def Generate_map():
    
    geojson_file = r"Data/Traffic_Lights.geojson"
    
    try:
        # Load the GeoJSON file
        gdf = gpd.read_file(geojson_file)

        
        if gdf.empty:
            st.error("The GeoJSON file is empty or not loaded properly.")
        else:
            # Convert GeoDataFrame to a Pandas DataFrame with latitude & longitude columns
            gdf["lon"] = gdf.geometry.x
            gdf["lat"] = gdf.geometry.y

            # Define Mapbox layer
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=gdf,
                get_position=["lon", "lat"],
                get_radius=50,  # Adjust point size
                get_color=[0, 122, 255, 200],  # Blue with transparency
                pickable=True,
            
            )

            # Define Mapbox view
            view_state = pdk.ViewState(
                latitude=gdf["lat"].mean(),
                longitude=gdf["lon"].mean(),
                zoom=11,
                pitch=0,
             
            )

            # Create the map
            map_deck = pdk.Deck(
                 map_style="mapbox://styles/mapbox/navigation-day-v1",  # Grey-White Theme
                layers=[layer],
              
                initial_view_state=view_state,
                tooltip={"text": "NAME: {SITE_NAME} \n NO: {SITE_NO}"},
                
            )

            
            st.pydeck_chart(map_deck)
    except Exception as e:
        st.error(f"Error loading GeoJSON file: {e}")