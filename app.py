
import streamlit as st
import sqlite3
import pandas as pd
import os

# Streamlit UI
st.title("📊 SQLite Database Viewer")

# User Input for Database File
db_path = st.text_input("Enter the path to your SQLite database file:", "")

if db_path:
    # Check if file exists
    if os.path.exists(db_path):
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]

            # If tables exist, let user select one
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
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
    else:
        st.error("Database file not found! Please enter a valid path.")

