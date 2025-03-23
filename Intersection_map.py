import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pydeck as pdk
import streamlit as st
def Generate_map(sites=None,all_sites=None,custom_sites=None,col1=None,zoom=11):
    
    geojson_file = r"Data/Traffic_Lights.geojson"
    
    try:
        # Load the GeoJSON file
        gdf = gpd.read_file(geojson_file)

        if type(sites) is int:
            gdf = gdf[gdf["SITE_NO"] == int(sites)]
        elif sites== "ALL SITES":
            sites_ints=[x for x in all_sites if isinstance(x, int) and not isinstance(x, bool)]
            gdf = gdf[gdf["SITE_NO"].isin(sites_ints)]
        elif custom_sites:
            filt_dict =  next((d for d in custom_sites if d["Name"] == sites),None)
            site_filters = filt_dict["Sites"]
            cust_sites= [x["Site"] for x in site_filters]
            
            gdf = gdf[gdf["SITE_NO"].isin(cust_sites)]
        
        
        if gdf.empty:
            st.error("The GeoJSON file is empty or not loaded properly.")
        else:
            # Convert GeoDataFrame to a Pandas DataFrame with latitude & longitude columns
            gdf["lon"] = gdf.geometry.x
            gdf["lat"] = gdf.geometry.y
            # Define Mapbox view
            view_state = pdk.ViewState(
                latitude=gdf["lat"].mean(),
                longitude=gdf["lon"].mean(),
                zoom=zoom,
                pitch=0,
             
            )
            zoom = view_state.zoom
            point_radius = 40 + zoom   # Adjust multiplier as necessary
            # Define Mapbox layer
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=gdf,
                get_position=["lon", "lat"],
                get_radius=point_radius,  # Adjust point size
                get_color=[0, 122, 255, 200],  # Blue with transparency
                pickable=True,
            
            )

            

            # Create the map
            map_deck = pdk.Deck(
                 map_style="mapbox://styles/mapbox/navigation-day-v1",  # Grey-White Theme
                layers=[layer],
              
                initial_view_state=view_state,
                tooltip={"text": "Site Name: {SITE_NAME} \n Site Number: {SITE_NO}"},
                
            )

            if col1:
                with col1:
                    st.pydeck_chart(map_deck)
            else:
                st.pydeck_chart(map_deck)
    except Exception as e:
        st.error(f"Error loading GeoJSON file: {e}")