import streamlit as st
import tempfile
import pandas as pd 
import numpy as np 
import sqlalchemy as db
from sqlalchemy import text
import datetime
import os
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

def Extract_from_dbs(dbfolder, sites, dates,message_placeholder ):
    # Loop over each date range
    for j,date_range in enumerate(dates):
        # Get start and end date
        startdate = date_range['Start_date']
        enddate = date_range['End_date']
        
        # Extract year from start and end date
        yearstart = startdate.year
        yearsend = enddate.year
        
        # Create year range
        years = range(yearstart, yearsend + 1)
        clean_data = pd.DataFrame()
        site_data = pd.DataFrame()

        # Generate site query using list join method for efficiency
        sitequery = " OR ".join([f"t1.NB_SCATS_SITE = {site}" for site in sites])
   
        # Format dates as strings
        startdate = startdate.strftime('%Y-%m-%d')
        enddate = enddate.strftime('%Y-%m-%d')

        # SQL query to get raw data
        sqlquery = f"""
        SELECT  t1.NB_SCATS_SITE || '_' || t1.Date as Reference, 
                t3.DOW as Weekday,
                STRFTIME('%m', t1.Date) as Month,
                t1.Date as Year,
                t1.NB_SCATS_SITE,
                t1.Date as QT_INTERVAL_COUNT,
                t1.NB_DETECTOR,
                t1.'00:00', t1.'00:15', t1.'00:30', t1.'00:45', t1.'01:00', 
                t1.'01:15', t1.'01:30', t1.'01:45', t1.'02:00', t1.'02:15', 
                t1.'02:30', t1.'02:45', t1.'03:00', t1.'03:15', t1.'03:30',
                t1.'03:45', t1.'04:00', t1.'04:15', t1.'04:30', t1.'04:45', 
                t1.'05:00', t1.'05:15', t1.'05:30', t1.'05:45', t1.'06:00', 
                t1.'06:15', t1.'06:30', t1.'06:45', t1.'07:00', t1.'07:15', 
                t1.'07:30', t1.'07:45', t1.'08:00', t1.'08:15', t1.'08:30', 
                t1.'08:45', t1.'09:00', t1.'09:15', t1.'09:30', t1.'09:45', 
                t1.'10:00', t1.'10:15', t1.'10:30', t1.'10:45', t1.'11:00', 
                t1.'11:15', t1.'11:30', t1.'11:45', t1.'12:00', t1.'12:15', 
                t1.'12:30', t1.'12:45', t1.'13:00', t1.'13:15', t1.'13:30', 
                t1.'13:45', t1.'14:00', t1.'14:15', t1.'14:30', t1.'14:45',
                t1.'15:00', t1.'15:15', t1.'15:30', t1.'15:45', t1.'16:00', 
                t1.'16:15', t1.'16:30', t1.'16:45', t1.'17:00', t1.'17:15', 
                t1.'17:30', t1.'17:45', t1.'18:00', t1.'18:15', t1.'18:30', 
                t1.'18:45', t1.'19:00', t1.'19:15', t1.'19:30', t1.'19:45',
                t1.'20:00', t1.'20:15', t1.'20:30', t1.'20:45', t1.'21:00', 
                t1.'21:15', t1.'21:30', t1.'21:45', t1.'22:00', t1.'22:15', 
                t1.'22:30', t1.'22:45', t1.'23:00', t1.'23:15', t1.'23:30', 
                t1.'23:45', t2.NM_REGION, t1.CT_RECORDS, t1.QT_VOLUME_24HOUR, 
                t1.CT_ALARM_24HOUR 
        FROM (RAW_DATA t1 
              LEFT JOIN Site_info t2 ON t1.NB_SCATS_SITE = t2.NB_SCATS_SITE) 
              LEFT JOIN Date_info t3 ON t1.Date = t3.Date  
        WHERE ({sitequery}) 
        AND (STRFTIME('%Y-%m-%d', t1.Date) BETWEEN '{startdate}' AND '{enddate}')
        AND ((t1.CT_ALARM_24HOUR = 0) AND (t1.CT_RECORDS > 0));"""
        
  
      
        
        for i,year in enumerate(years):
            db_path = os.path.join(dbfolder, f"Scats{year}.db")
            if not os.path.exists(db_path):
                message_placeholder.text(f"Database Scats{year}.db does not exist. Skipping...")
                
                continue  # Skip this iteration and move to the next year
            message_placeholder.text(f'Extracting data from Scats{year}.db')
            engine = db.create_engine(f"sqlite+pysqlite:///{db_path}", future=True)
            
            
     
            with engine.begin() as cn:
               
                dataframe = pd.read_sql(text(sqlquery), cn)
                if (i == 0) & (j == 0):
                    clean_data = dataframe
              
                else:
              
                    clean_data = pd.concat([clean_data, dataframe], ignore_index=True)
                 
                 
    return clean_data

def Extract_from_dbs_custom(dbfolder, sites, dates,message_placeholder):
    # Initialize clean_data to collect results across all years and date ranges
    clean_data = pd.DataFrame()
    
    # Loop over each date range
    for j, date_range in enumerate(dates):
        # Get start and end date
        startdate = date_range['Start_date']
        enddate = date_range['End_date']
        
        # Extract year from start and end date
        yearstart = startdate.year
        yearsend = enddate.year
        
        # Create year range
        years = range(yearstart, yearsend + 1)

        # Format dates as strings
        startdate = startdate.strftime('%Y-%m-%d')
        enddate = enddate.strftime('%Y-%m-%d')

        # Loop over each year
        for i, year in enumerate(years):
            db_path = os.path.join(dbfolder, f"Scats{year}.db")
            if not os.path.exists(db_path):
                message_placeholder.text(f"Database Scats{year}.db does not exist. Skipping...")
                
                continue  # Skip this iteration and move to the next year
            message_placeholder.text(f'Extracting data from Scats{year}.db')
          
            engine = db.create_engine(f"sqlite+pysqlite:///{db_path}", future=True)
            
            # Generate sitequery to include both site and detector conditions
            sitequeries = []
            for site_entry in sites:
                site_name = site_entry["Name"]
                for site_info in site_entry["Sites"]:
                    site_id = site_info["Site"]
                    detectors = site_info["Detectors"]
                    
                    # Generate condition for each site and its detectors
                    detector_conditions = " OR ".join([f"t1.NB_DETECTOR = {detector}" for detector in detectors])
                    sitequeries.append(f"({detector_conditions}) AND t1.NB_SCATS_SITE = {site_id}")
            
            # Join the site queries for the WHERE condition
            sitequery = " OR ".join(sitequeries)

            # SQL query to get raw data
            sqlquery = f"""
            SELECT  t1.NB_SCATS_SITE || '_' || t1.Date as Reference, 
                    t3.DOW as Weekday,
                    STRFTIME('%m', t1.Date) as Month,
                    t1.Date as Year,
                    t1.NB_SCATS_SITE,
                    t1.Date as QT_INTERVAL_COUNT,
                    t1.NB_DETECTOR,
                    t1.'00:00', t1.'00:15', t1.'00:30', t1.'00:45', t1.'01:00', 
                    t1.'01:15', t1.'01:30', t1.'01:45', t1.'02:00', t1.'02:15', 
                    t1.'02:30', t1.'02:45', t1.'03:00', t1.'03:15', t1.'03:30',
                    t1.'03:45', t1.'04:00', t1.'04:15', t1.'04:30', t1.'04:45', 
                    t1.'05:00', t1.'05:15', t1.'05:30', t1.'05:45', t1.'06:00', 
                    t1.'06:15', t1.'06:30', t1.'06:45', t1.'07:00', t1.'07:15', 
                    t1.'07:30', t1.'07:45', t1.'08:00', t1.'08:15', t1.'08:30', 
                    t1.'08:45', t1.'09:00', t1.'09:15', t1.'09:30', t1.'09:45', 
                    t1.'10:00', t1.'10:15', t1.'10:30', t1.'10:45', t1.'11:00', 
                    t1.'11:15', t1.'11:30', t1.'11:45', t1.'12:00', t1.'12:15', 
                    t1.'12:30', t1.'12:45', t1.'13:00', t1.'13:15', t1.'13:30', 
                    t1.'13:45', t1.'14:00', t1.'14:15', t1.'14:30', t1.'14:45',
                    t1.'15:00', t1.'15:15', t1.'15:30', t1.'15:45', t1.'16:00', 
                    t1.'16:15', t1.'16:30', t1.'16:45', t1.'17:00', t1.'17:15', 
                    t1.'17:30', t1.'17:45', t1.'18:00', t1.'18:15', t1.'18:30', 
                    t1.'18:45', t1.'19:00', t1.'19:15', t1.'19:30', t1.'19:45',
                    t1.'20:00', t1.'20:15', t1.'20:30', t1.'20:45', t1.'21:00', 
                    t1.'21:15', t1.'21:30', t1.'21:45', t1.'22:00', t1.'22:15', 
                    t1.'22:30', t1.'22:45', t1.'23:00', t1.'23:15', t1.'23:30', 
                    t1.'23:45', t2.NM_REGION, t1.CT_RECORDS, t1.QT_VOLUME_24HOUR, 
                    t1.CT_ALARM_24HOUR 
            FROM (RAW_DATA t1 
                LEFT JOIN Site_info t2 ON t1.NB_SCATS_SITE = t2.NB_SCATS_SITE) 
                LEFT JOIN Date_info t3 ON t1.Date = t3.Date  
            WHERE ({sitequery}) 
            AND (STRFTIME('%Y-%m-%d', t1.Date) BETWEEN '{startdate}' AND '{enddate}')
            AND ((t1.CT_ALARM_24HOUR = 0) AND (t1.CT_RECORDS > 0));"""
            
            # Execute the query and load data
            with engine.begin() as cn:
                dataframe = pd.read_sql(text(sqlquery), cn)
                if i == 0 and j == 0:
                    clean_data = dataframe
                else:
                    clean_data = pd.concat([clean_data, dataframe], ignore_index=True)
    
    return clean_data
    


    