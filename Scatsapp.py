'''
SCATS DASHBOARD: BETA VERSION
LAST UPDATED: 10/03/2025

MADE BY: Matthew Bentham


'''


#Library Imports ---------------------------------------------------
import streamlit as st
import sqlite3
import geopandas as gpd
import folium
import pandas as pd
import os
from data_comparison import intTab2
from IntProfile import intTab
from filters import Main_filters
from filedialog import upload_csv_button
from Intersection_map import Generate_map
from Db_functions import import_file_paths,Extract_from_dbs,Extract_from_dbs_custom
import tempfile
#---------------------------------------------------------------------
st.set_page_config(page_title='S.C.A.T.S', page_icon="📊", initial_sidebar_state="expanded", layout='wide')
# LOAD EXTERNAL CSS FOR STYLING
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path=os.path.join('assets','style.css')
load_css(css_path)

if "page" not in st.session_state:
    st.session_state.page = 0

# PAGE SETUP _______________________________________________________________________

st.markdown(
        """
        <h1 class="Title",style="text-align: left; margin-top: 0;">
            S.C.A.T.S Dashboard Tool
        </h1>
        """,
        unsafe_allow_html=True
    )

#_____________________________________________________________________________________

# CSV INPUTS AND FILTERING 

if st.session_state.page == 0:
    
    if "file_path" not in st.session_state:
        st.session_state.file_path = None 
    if "filters" not in st.session_state:
        st.session_state.filters = None  
    col1, col2= st.columns([1,2])
    # Upload a CSV file using the button
    uploaded_file = upload_csv_button(col1)
    with col2:
        Generate_map(zoom=11)
    # If file is uploaded, store it in session state
    if uploaded_file:
        st.session_state.file_path = uploaded_file

    # If a file is selected
    if st.session_state.get('file_path') is not None:
        with col1:
            st.session_state.filters = Main_filters()
            if st.session_state.get('filters') is not None:
                
                st.session_state.page = 1
                st.rerun()

   
#_____________________________________________________________________________________

# AFTER FILE INFO SUBMITTED SHOW DASHBOARD TABS

elif st.session_state.page == 1:
   
   
    tab1, tab2 = st.tabs(["Intersection Profile", " Data Comparison"])

   
    
    intTab(tab1)
    intTab2(tab2)
