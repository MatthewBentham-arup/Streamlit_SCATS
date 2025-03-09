'''
SCATS DASHBOARD: BETA VERSION
LAST UPDATED: 8/03/2025

MADE BY: Matthew Bentham


'''


#Library Imports
import streamlit as st
import sqlite3
import tkinter

import pandas as pd
import os
from IntProfile import intTab
from filters import Main_filters
from filedialog import upload_folder_button
from Db_functions import import_file_paths,Extract_from_dbs,Extract_from_dbs_custom

import tempfile
st.set_page_config(page_title='S.C.A.T.S', page_icon="📊", initial_sidebar_state="expanded", layout='wide')
# LOAD EXTERNAL CSS FOR STYLING
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path=os.path.join('assets','style.css')
load_css(css_path)


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
Data_created = False

# Streamlit UI
if "folder_path" not in st.session_state:
    st.session_state.folder_path = None  # Default is None until a folder is selected

# Select a folder using the button
folder_path = upload_folder_button()

# If folder is selected, store it in session state
if folder_path:
    st.session_state.folder_path = folder_path


if  st.session_state['folder_path']:
    filters = Main_filters()
    if filters:
        dates = filters[0][0]['Dates']
        filter_type = filters[2]
        sites = filters[1]
        message_placeholder = st.empty()
        message_placeholder.text("Processing DB files...")
        if filter_type =="Sites":
            site_numbers = [site['siteno'] for site in sites['sites']]
            
            data = Extract_from_dbs(st.session_state.folder_path, site_numbers, dates,message_placeholder)
            message_placeholder.text("Task completed!")
            if data.empty:
                st.error("Database contains no data for the selected filters. Please ensure the .db files contains the required information")
            st.text(data)
        elif filter_type =="Custom":
            data = Extract_from_dbs_custom(st.session_state.folder_path, sites, dates,message_placeholder)
            st.success("Extracted Data!")
            if data.empty:
                    st.error("Database contains no data for the selected filters. Please ensure the .db files contains the required information")
        
        
            
            



if Data_created:
        tab1, tab2 = st.tabs(["Intersection Profile", "Data Comparison"])

        intTab(tab1)

# Streamlit UI
