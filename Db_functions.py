import streamlit as st
import tempfile

'''
Description: This script contains all methods relating to the querying and importing of db files


'''

def import_file_paths(db_files):
    
    if db_files:
        # Create a dictionary to store table names from both databases
        db_tables = {}

        for db_file in db_files:
           
            # Create a temporary file to store the uploaded SQLite file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as temp_file:
                temp_file.write(db_file.getbuffer())
                temp_file_path = temp_file.name  # Store the temp file path
        return temp_file_path

              
    else:
        st.info("Please upload one or more SQLite database files to get started.")

    