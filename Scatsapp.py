'''
SCATS DASHBOARD: BETA VERSION
LAST UPDATED: 8/03/2025

MADE BY: Matthew Bentham


'''


#Library Imports
import streamlit as st
import sqlite3


import pandas as pd
import os
from IntProfile import intTab
from filters import Main_filters
from filedialog import upload_csv_button
from Db_functions import import_file_paths,Extract_from_dbs,Extract_from_dbs_custom
import tempfile
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
st.markdown("""
        <style>
               /* Remove blank space at top and bottom */ 
               .block-container {
                   padding-top: 1rem;
                   padding-bottom: 0rem;
                }

        </style>
        """, unsafe_allow_html=True)
st.markdown(
        """
        <h1 style="text-align: left; margin-top: 0;">
            S.C.A.T.S Dashboard Tool
        </h1>
        """,
        unsafe_allow_html=True
    )

#_____________________________________________________________________________________

# DB INPUTS AND FILTERING:


if st.session_state.page == 0:
    if "file_path" not in st.session_state:
        st.session_state.file_path = None  # Default is None until a file is selected
    if "filters" not in st.session_state:
        st.session_state.filters = None  # Default is None until a file is selected

    # Upload a CSV file using the button
    
    uploaded_file = upload_csv_button()

    # If file is uploaded, store it in session state
    if uploaded_file:
        st.session_state.file_path = uploaded_file

    # If a file is selected
    if st.session_state.get('file_path') is not None:
        st.session_state.filters = Main_filters()
        if st.session_state.get('filters') is not None:
            
            st.session_state.page = 1
            st.rerun()

elif st.session_state.page == 1:
   
    # Call clear_all_except_file to reset everything except the file
    
    # Create tabs for the UI
    tab1, tab2 = st.tabs(["Intersection Profile", "Data Comparison"])

    # Call your specific function to handle the content of each tab
    intTab(tab1)
