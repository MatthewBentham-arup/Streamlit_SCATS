import streamlit as st


import sqlite3
import pandas as pd
import streamlit as st

def upload_csv_button(col1):
    # Add an icon for the file upload button
    upload_icon = "📄"  # You can use other symbols or Font Awesome icons if needed
    with col1:
        with st.expander("Info ❓", expanded=False):
            st.markdown(
    "<p>Version: <b>1.0 Beta</b> <br>"
    "This is a <b>dashboard generator</b> specifically designed for <b>ARUP internal use</b>. "
    "<br>Inputs require the use of <b>ARUP's internal SCATS database tool</b>.</p>"
    
    "<p><b>Steps:</b></p>"
    "<ol>"
    "<li><b>Step 1:</b> Use the SCATS Processing Tool and extract the cleaned data (currently not developed for use with raw data) for the required dates and sites.</li>"
    "<li><b>Step 2:</b> Input this data into this webpage.</li>"
    "<li><b>Step 3:</b> Choose a filtering option: <br>"
    "<b>SITES:</b> The resultant dashboard will filter ONLY on site number. <br>"
    "<b>Custom filter:</b> Allows you to create a list of dictionaries if you wish to do more complicated filtering.</li>"
    "</ol>"
      "<p><b>Developed by:</b> Matthew Bentham</p>",
    unsafe_allow_html=True
)


        st.warning(
            "⚠️ Please upload SCATS data Extracted from SCATS DATABASE TOOL"
        )
    
    
        # Allow the user to upload a CSV file
        with st.spinner('Please wait, uploading the file...'):
            uploaded_file = st.file_uploader(f'{upload_icon} Upload Clean_Data_extracted', type='csv')
        
        if uploaded_file:
            # Read the uploaded CSV into a pandas DataFrame
            df = pd.read_csv(uploaded_file)
        

            # Filter columns that contain ':' and are not in the exclusion list
            filtered_cols = df.columns[df.columns.str.contains(":") ].tolist()
            df_cleaned = df[~df[filtered_cols].isin([-1]).any(axis=1)]
            

        
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








