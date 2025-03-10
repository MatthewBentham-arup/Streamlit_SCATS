import streamlit as st
import json
from datetime import date, timedelta

"""
FILTERS

this Script holds all methods relating to the filter of data before data is extracted from the databases

"""
today = date.today()
last_year = today.replace(year=today.year - 1)

class FilterClass:
    def __init__(self, value=None):
        self.value = value
        # Initialize session state filter if it doesn't exist
        if "filter" not in st.session_state:
            st.session_state.filter = {
                "Site_no": 0,
                "Start_date": last_year,
                "End_date": today,
                "Rolling_vol":60,
                "Survey_Date":today
            }

    def display_filters(self, sites,idval,comparison=False):
        # Dropdown to filter on site
        
        with st.expander("Filters", expanded=True):
            # Set Site_no filter in session state
            st.session_state.filter["Site_no"] = st.selectbox("Filter on Site", sites,key=f'select {idval}')
            
            # Set start and end date filters
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.filter["Start_date"] = st.date_input(
                    "Start Date", 
                    value=st.session_state.filter["Start_date"], 
                    key=f'sdate {idval}'
                )
            with col2:
                st.session_state.filter["End_date"] = st.date_input(
                    "End Date", 
                    value=st.session_state.filter["End_date"], 
                    key=f'edate {idval}'
                )

            
            
            if comparison:
                st.session_state.filter["Survey_Date"] = st.date_input(
                    "Survey Date", 
                    value=st.session_state.filter["Survey_Date"], 
                    key=f'Survey_Date {idval}'
                )
            else:
                st.session_state.filter["Rolling_vol"]=st.slider("Rolling Volume Time Interval (mins)",min_value=15,max_value=1440,value=60,step=15,key=f'roll {idval}')


            # Update the value attribute with the current filter state
            self.value = st.session_state.filter



class SiteForm:
    def __init__(self,value=None):
        self.value = value
        # Ensure session state is initialized correctly
        if "input_rows" not in st.session_state:
            today = datetime.today()
            last_year = today - timedelta(days=365)
            st.session_state.input_rows = [{"sites": [{"siteno": 0}]}]

    def add_site(self):
        st.session_state.input_rows[0]["sites"].append({"siteno": 0})  # Add a new site
        st.rerun()

    def remove_site(self):
        if len(st.session_state.input_rows[0]["sites"]) > 1:  # Prevent removing last site
            st.session_state.input_rows[0]["sites"].pop()
            st.rerun()

    def display_sites(self):
     

        with st.expander("List All Sites You Wish to View",expanded=True):
            for j, field in enumerate(st.session_state.input_rows[0]["sites"]):
                field["siteno"] = st.number_input(
                    f"SITE NO (SITE {j+1})", value=field["siteno"], key=f"site_{j}", step=1, format="%d"
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add More Sites"):
                    self.add_site()
            with col2:
                if st.button("🗑️ Remove Last Site"):
                    self.remove_site()
            self.value = st.session_state.input_rows[0]

class DateRanges:
    def __init__(self, value=None):
        self.value = value
        # Ensure session state is initialized correctly
        if "Dates" not in st.session_state:
            today = datetime.today()
            last_year = today - timedelta(days=365)
            st.session_state.Dates = [{"Dates": [{"Start_date": last_year, "End_date": today}]}]

    def add_date(self):
        today = datetime.today()
        last_year = today - timedelta(days=365)
        st.session_state.Dates[0]["Dates"].append({"Start_date": last_year, "End_date": today})  
        st.rerun()

    def remove_date(self):
        if len(st.session_state.Dates[0]["Dates"]) > 1:  # Prevent removing the last date range
            st.session_state.Dates[0]["Dates"].pop()
            st.rerun()

    def display_dates(self):
        with st.expander("List All Date Ranges you wish to view",expanded=True):
            for j, field in enumerate(st.session_state.Dates[0]["Dates"]):
                col1, col2 = st.columns(2)
                with col1:
                    field["Start_date"] = st.date_input(
                        f"Start Date (Range {j+1})", 
                        value=field["Start_date"], 
                        key=f"start_date_{j}"
                    )
                with col2:
                    field["End_date"] = st.date_input(
                        f"End Date (Range {j+1})", 
                        value=field["End_date"], 
                        key=f"end_date_{j}"
                    )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add More Ranges"):
                    self.add_date()
                    
            with col2:
                if st.button("🗑️ Remove Last Range"):
                    self.remove_date()
            self.value = st.session_state.Dates


class custom_sites_form:
    def __init__(self,value=None):
        # Ensure session state is initialized correctly
        self.value = value
        if "Detector_group" not in st.session_state:
            st.session_state.Detector_group = []
        
    def add_site(self,json):
        st.session_state.Detector_group.append(json)  # Add a new site
        st.rerun()
    def check_format(self,data):
        """
        Validates whether the input JSON follows the expected structure:
        {
            "Name": str,
            "Sites": [
                {"Site": int, "Detectors": [int, int, ...]},
                ...
            ]
        }
        """
        if not isinstance(data, list):
            return False, st.error("Input must be a list.")
        for dict1 in data:
            if not isinstance(dict1, dict):
                return False, st.error("Input must be a dictionary.")

            if "Name" not in dict1 or not isinstance(dict1["Name"], str):
                return False, st.error("Missing or invalid 'Name' field (must be a string).")

            if "Sites" not in dict1 or not isinstance(dict1["Sites"], list):
                return False, st.error("Missing or invalid 'Sites' field (must be a list).")

            for site in dict1["Sites"]:
                if not isinstance(site, dict):
                    return False, st.error("Each site must be a dictionary.")
                if "Site" not in site or not isinstance(site["Site"], int):
                    return False, st.error("Each site must have a 'Site' field (integer).")
                if "Detectors" not in site or not isinstance(site["Detectors"], list):
                    return False, st.error("Each site must have a 'Detectors' field (list).")
                if not all(isinstance(detector, int) for detector in site["Detectors"]):
                    return False, st.error("All detectors must be integers.")

        return True, "Valid format."




    def display_sites(self):

        
        with st.expander(f"Please Insert Custom Detector Group",expanded=True):
            user_input = st.text_area(
            "Enter a list of dictionaries (JSON format):",
            placeholder='[{"Name": "West Approach", "Sites": [{"Site": 1125, "Detectors": [1, 2,3,4,5,5]},{"Site": 2245, "Detectors": [12,13]}]}]',
            height=100  
        )
        if user_input:
        # Convert input to dictionary
            try:
                data = json.loads(user_input) if user_input else []
                st.session_state.Detector_group.append(data)
                self.check_format(data)
                self.value = data
                
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your input.")
    



def Main_filters():
    
    
    Filter_type = st.selectbox("Filter Type",("By Sites","By Custom Detector Groups"))


    if Filter_type =="By Sites":
        typef="Sites"
        value=None
    else:
        typef="Custom"
        form = custom_sites_form()
        form.display_sites() 
        value = None
    

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if st.button("✅ Submit"):
            st.session_state.submitted = True  # Set flag indicating the form is submitted
            
    if st.session_state.submitted:
          
            return value,typef
  
    

