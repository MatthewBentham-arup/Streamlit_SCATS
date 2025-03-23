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
                "Survey_filt":"Survey Date",
                "Survey_Date":today,
                "Survey_volume":0,
            }

    def display_filters(self, sites,idval,max_date,min_date,comparison=False):
        # Dropdown to filter on site
        
        
        # Set Site_no filter in session state
        st.session_state.filter["Site_no"] = st.selectbox("Filter on Site", sites,key=f'select {idval}')
        
        # Set start and end date filters
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.filter["Start_date"] = st.date_input(
                "Start Date", 
                value=min_date, 
                key=f'sdate {idval}'
            )
        with col2:
            st.session_state.filter["End_date"] = st.date_input(
                "End Date", 
                value=max_date, 
                key=f'edate {idval}'
            )

        
        
        if comparison:
            st.session_state.filter["Survey_filt"] = st.selectbox("Comparison Type", ['Survey Date','Mannual Input'],key=f'select2 {idval}')
            if st.session_state.filter["Survey_filt"] == 'Survey Date':
                st.session_state.filter["Survey_Date"] = st.date_input(
                    "Survey Date", 
                    value=st.session_state.filter["Survey_Date"], 
                    key=f'Survey_Date {idval}'
                )
            else:
                st.session_state.filter["Survey_volume"] = st.number_input(
                    "Volume to Compare", 
                    value=0, 
                    key=f'Survey_vol {idval}'
                )
        else:
            st.session_state.filter["Rolling_vol"]=st.slider("Rolling Volume Time Interval (mins)",min_value=15,max_value=1440,value=60,step=15,key=f'roll {idval}')


        # Update the value attribute with the current filter state
        self.value = st.session_state.filter


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
        if not data:
                return False, st.error("List contains no dictionary")
        
        for dict1 in data:
           
            

            if not isinstance(dict1, dict):
                return False, st.error("Input must be a dictionary.")

            if "Name" not in dict1 or not isinstance(dict1["Name"], str):
                return False, st.error("Missing or invalid 'Name' field (must be a string).Check Spelling")

            if not dict1["Name"]:
                return False, st.error("Missing 'Name' Value.")

            if "Sites" not in dict1 or not isinstance(dict1["Sites"], list):
                return False, st.error("Missing or invalid 'Sites' field (must be a list).Check Spelling")

            if not dict1["Sites"]:
                return False, st.error("Missing 'Sites' Values.")

            for site in dict1["Sites"]:
                if not isinstance(site, dict):
                    return False, st.error("Each site must be a dictionary.")
                if not site["Site"]:
                    return False, st.error("Missing 'Sites' Values.")
                if "Site" not in site or not isinstance(site["Site"], int):
                    return False, st.error("Each site must have a 'Site' field (integer). Check Spelling of 'Site'")
                if "Detectors" not in site or not isinstance(site["Detectors"], list):
                    return False, st.error("Each site must have a 'Detectors' field (list).Check Spelling")
                if not site["Detectors"]:
                    return False, st.error(f"Missing Detector numbers for {site['Site']}.")
                if not all(isinstance(detector, int) for detector in site["Detectors"]):
                    return False, st.error("All detectors must be integers.")

        return True, "Valid format."

    



    def display_sites(self):

        
        with st.expander(f"Please Insert Custom Detector Group",expanded=True):
            user_input = st.text_area(
            "Enter a list of dictionaries (JSON format):",
            placeholder='[{"Name": "West Approach", "Sites": [{"Site": 1125, "Detectors": [1, 2,3,4,5]},{"Site": 2245, "Detectors": [12,13]}]}]',
            height=100  
        )
            error=False
            if user_input:
            # Convert input to dictionary
                try:
                    
                    data = json.loads(user_input) if user_input else []
                    
                    st.session_state.Detector_group.append(data)
                    self.value = data
                    error,msg= self.check_format(data)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format. Please check your input.")
                    error=False

        return error
        



def Main_filters():
    
    
    Filter_type = st.selectbox("Filter Type",("By Sites","By Custom Detector Groups"))

    error=True
    if Filter_type =="By Sites":
        typef="Sites"
        value=None
    else:
        typef="Custom"
        form = custom_sites_form()
        error  = form.display_sites() 
        value = None
    

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if st.button("✅ Submit"):
            if error==True:
                st.session_state.submitted = True  # Set flag indicating the form is submitted
            else:
                st.error("Invalid JSON format. Please check your input.")
            
    if st.session_state.submitted:
          
            return value,typef
  
    

