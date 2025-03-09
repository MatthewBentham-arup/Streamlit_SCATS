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
from Db_functions import import_file_paths
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




# User Input for Multiple Database Files (using file uploader with multiple selection)
db_files = st.file_uploader("Choose one or more SQLite database files:", type=["sqlite", "db"], accept_multiple_files=True)
files = import_file_paths(db_files)
#st.text(files)
if files:
    filters = Main_filters()
    if filters:
        dates = filters[0][0]['Dates']
        filter_type = filters[2]
        sites = filters[1]
        st.text(dates)
if Data_created:
        tab1, tab2 = st.tabs(["Intersection Profile", "Data Comparison"])

        intTab(tab1)

# Streamlit UI