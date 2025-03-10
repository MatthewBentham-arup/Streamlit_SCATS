import streamlit as st


import sqlite3
import pandas as pd
import streamlit as st

def upload_csv_button():
    # Add an icon for the file upload button
    upload_icon = "📄"  # You can use other symbols or Font Awesome icons if needed
    
    st.warning(
        "⚠️ Please upload SCATS data Extracted from SCATS DATABASE TOOL"
    )
    
    # Allow the user to upload a CSV file
    with st.spinner('Please wait, uploading the file...'):
        uploaded_file = st.file_uploader(f'{upload_icon} Upload Clean_Data_extracted', type='csv')
        
    if uploaded_file:
        # Read the uploaded CSV into a pandas DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Connect to SQLite (or create the database if it doesn't exist)
        conn = sqlite3.connect("index.db")
        cursor = conn.cursor()
        
        # Create a table based on the DataFrame's columns if it doesn't exist
        df.to_sql("scats_data", conn, if_exists="replace", index=False)
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()

        st.success("File uploaded and data stored in index.db")
        
    return uploaded_file  # Return the uploaded file object for further use








