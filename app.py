import streamlit as st
import sqlite3
import pandas as pd
import os
import tempfile

# Streamlit UI
st.title("📊 SQLite Database Viewer")

# User Input for Database File (using file uploader instead of text input)
db_file = st.file_uploader("Choose an SQLite database file:", type=["sqlite", "db"])

if db_file:
    try:
        # Create a temporary file to store the uploaded SQLite file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as temp_file:
            temp_file.write(db_file.getbuffer())
            temp_file_path = temp_file.name  # Store the temp file path

        # Connect to the database
        conn = sqlite3.connect(temp_file_path)
        cursor = conn.cursor()

        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]

        # If tables exist, let the user select one
        if tables:
            selected_table = st.selectbox("Select a table to display:", tables)

            # Load table into a DataFrame
            query = f"SELECT * FROM {selected_table}"
            df = pd.read_sql_query(query, conn)

            # Display table
            st.write(f"### 📌 Data from `{selected_table}` table:")
            st.dataframe(df)

        else:
            st.warning("No tables found in this database.")

        conn.close()
        # Remove the temporary file after use
        os.remove(temp_file_path)
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
else:
    st.info("Please upload an SQLite database file to get started.")
