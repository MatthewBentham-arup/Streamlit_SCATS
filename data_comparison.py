import streamlit as st
import pandas as pd
from filters import FilterClass
from Db_functions import retrieve_data_from_db
import altair as alt
import datetime
'''
Int Profile: 
This script is used for all functions pertaining to the Data Comparison with 30th Bussiest day

'''

# HELPER FUNCTIONS -----------------------------------------------------------------
def group_and_sum_exclude(df, group_column, exclude_columns=[]):
    # Identify numerical columns
    numeric_columns = df.select_dtypes(include=['number']).columns
    
    # Remove excluded columns from numeric columns
    numeric_columns_to_sum = [col for col in numeric_columns if col not in exclude_columns]
    
    # Group by the specified column and aggregate
    grouped = df.groupby(group_column).agg(
        {col: 'sum' for col in numeric_columns_to_sum}  # Sum numerical columns
    )
    
    
    for col in exclude_columns:
        grouped[col] = df.groupby(group_column)[col].last()  # Keep the last non-numeric value

    return grouped
def get_rank_data(data,rank_value):
    # Get the row where the rank matches
    result = data.loc[data['Rank'] == rank_value]
    
    # If there's no result, return "-" for both the index and the volume
    if result.empty:
        return "-", "-"
    
    # Otherwise, return the first value of the index and 'Total Daily Volume'
    return result.index[0], result['Total Daily Volume (Veh)'].iloc[0]
def add_rank_column(data):
    data['Rank'] = data['Total Daily Volume (Veh)'].rank(method="first", ascending=False)

    data=data.sort_values("Rank")
    return data
def generate_summary_dicts(data):
    Int_vol_dict={'Busiest day':[],'30 Busiest day':[],'100 Busiest day':[],'90th Percentile':0,'50th Percentile':0,'Average':0}
    
    Int_vol_dict['Busiest day'] = get_rank_data(data,1)
    Int_vol_dict['30 Busiest day'] = get_rank_data(data,30)
    Int_vol_dict['100 Busiest day'] = get_rank_data(data,100)
   
    Int_vol_dict['90 Percentile'] = data['Total Daily Volume (Veh)'].quantile(0.9)
    Int_vol_dict['50 Percentile'] = data['Total Daily Volume (Veh)'].quantile(0.5)
    Int_vol_dict['Average'] = data['Total Daily Volume (Veh)'].mean()
    try:
        survey_date = st.session_state.filter["Survey_Date"].strftime('%d/%m/%Y')
        survey_vol=data.loc[data.index == str(survey_date)]['Total Daily Volume (Veh)'][0]
        perc_dif = ((survey_vol)/Int_vol_dict['30 Busiest day'][1]-1)*100
        factor = ((Int_vol_dict['30 Busiest day'][1])/survey_vol)
        int_survey_dict={'volume':round(survey_vol),'diff_30':round(perc_dif,2),'factor':round(factor,2)}
    except:
         int_survey_dict={'volume':"Not in data",'diff_30':"Not in data",'factor':"Not in data"}

    return Int_vol_dict,int_survey_dict

def Get_unique_sites(data,custom=None):
    sites=data['NB_SCATS_SITE'].unique().tolist()
    sites.append('ALL SITES')
    if custom:
        for name in custom:
            sites.append(name)
    return sites
def transform_table(orig_df,Int_vol_dict,int_survey_dict):
    
    # Build the HTML table string with merged headers
    table_1_html = f"""
<table id="summary">
    <thead>
      <tr>
        <th colspan="7">Summary of Intersection Volumes</th>
      </tr>
      <tr>
        <th>Description</th>
        <th>Rank</th>
        <th>Date</th>
        <th>Volume</th>
      </tr>
    </thead>
    <tbody>
      <!-- Table body content goes here -->
      <tr>
        <td>Busiest day</td>
        <td>1</td>
        <td>{Int_vol_dict['Busiest day'][0]}</td>
        <td>{Int_vol_dict['Busiest day'][1]}</td>
      </tr>
      <tr>
        <td>30 Busiest day</td>
        <td>30</td>
        <td>{Int_vol_dict['30 Busiest day'][0]}</td>
        <td>{Int_vol_dict['30 Busiest day'][1]}</td>
      </tr>
      <tr>
        <td>100 Busiest day</td>
        <td>100</td>
        <td>{Int_vol_dict['100 Busiest day'][0]}</td>
        <td>{Int_vol_dict['100 Busiest day'][1]}</td>
      </tr>
      <tr>
        <td colspan="3">90th percentile</td>
         <td>{round(Int_vol_dict['90 Percentile'])}</td>
      </tr>
      <tr>
        <td colspan="3">50th percentile (median)</td>
        <td>{round(Int_vol_dict['50 Percentile'])}</td>
      </tr>
      <tr>
         <td colspan="3">Average</td>
        <td>{round(Int_vol_dict['Average'])}</td>
      </tr>
    </tbody>
</table>
"""

# HTML for the second table (Seasonality scaling factor to 30th busiest day)
    table_2_html = f"""
<table id="summary" style="margin-bottom: 306px;">
    <thead>
      <tr>
        <th colspan="7">Seasonality scaling factor to 30th busiest day</th>
      </tr>
      <tr>
        <th>Description</th>
        <th>Volume</th>
        <th>% Diff to 30th Busiest</th>
        <th>Scaling factor</th>
      </tr>
    </thead>
    <tbody>
      <!-- Table body content goes here -->
      <tr>
        <td>Survery Day</td>
        <td>{int_survey_dict['volume']}</td>
        <td>{int_survey_dict['diff_30']} %</td>
        <td>{int_survey_dict['factor']}</td>
      </tr>
    </tbody>
</table>
"""

    
    return table_1_html,table_2_html
   
    
    


def Get_daily_average(filter_on,data,custom_sites):
    
    # Site Filtering ---------------------------------------------------------------------------
    exclude_in_sum=["Month","NB_SCATS_SITE","NB_DETECTOR","Weekday","Year","QT_INTERVAL_COUNT"]
    site_filter = filter_on.value["Site_no"]

    if type(site_filter) is int:
        # FILTER ON SITE:
        filtered_data = data.loc[data['NB_SCATS_SITE']==site_filter]
    elif site_filter== "ALL SITES":
        filtered_data=data
    elif custom_sites:
        filt_dict =  next((d for d in custom_sites if d["Name"] == site_filter),None)
        site_filters = filt_dict["Sites"]

        filter_query = False  # Start with a base condition (all False)

        for site_filter in site_filters:
            site_f = site_filter["Site"]
            detects = site_filter["Detectors"]
            filter_query |= (data['NB_SCATS_SITE'] == site_f) & (data['NB_DETECTOR'].isin(detects))

        filtered_data = data.loc[filter_query]




    if filtered_data.empty:
        st.error("No data matching filters")
    else:
        # Date Filtering ---------------------------------------------------------------------------
        filtered_data["QT_INTERVAL_COUNT"] = pd.to_datetime(filtered_data["QT_INTERVAL_COUNT"])
        
        is_between_dates = (filtered_data["QT_INTERVAL_COUNT"] > datetime.datetime.combine(filter_on.value["Start_date"], datetime.datetime.min.time())) & (filtered_data["QT_INTERVAL_COUNT"] < datetime.datetime.combine(filter_on.value["End_date"], datetime.datetime.min.time()) )
        filtered_data=filtered_data.loc[is_between_dates]

        # Group by date ---------------------------------------------------------------------------
        aggregated_data=group_and_sum_exclude(filtered_data,"QT_INTERVAL_COUNT",exclude_in_sum)
        aggregated_data=aggregated_data.reset_index(drop=True)
        aggregated_data["Date"]= aggregated_data["QT_INTERVAL_COUNT"].dt.strftime('%d/%m/%Y')
        aggregated_data=aggregated_data.set_index(["Date"])
       
        # only include volume column
        aggregated_data = aggregated_data[["QT_VOLUME_24HOUR","Weekday"]].rename(columns={"QT_VOLUME_24HOUR": "Total Daily Volume (Veh)"})
        aggregated_data=add_rank_column(aggregated_data)

        
        Int_vol_dict,int_survey_dict=generate_summary_dicts(aggregated_data)
        # Get summary values -------------------------------------------------------------------------
       


        #transform table ------------------------------------------------------------------------------
        table_1_html,table_2_html=transform_table(aggregated_data,Int_vol_dict,int_survey_dict)

        return table_1_html,table_2_html,aggregated_data
       

#-------------------------------------------

# LINE PLOT CODE

#--------------------------------------------

def generate_barplot_data(data):
    survey_date = st.session_state.filter["Survey_Date"].strftime('%d/%m/%Y')
    survey_vol = None
    survey_rank = None
    # Create a new column to differentiate Rank 30 for coloring
    if str(survey_date) in data.index:
        survey_vol = data.loc[data.index == str(survey_date)]['Total Daily Volume (Veh)'].iloc[0]
        survey_rank = int(data.loc[data['Total Daily Volume (Veh)'] == survey_vol]['Rank'].iloc[0])
    
    # Create a new column to differentiate Rank 30 and survey rank for coloring
    data['color'] = data['Rank'].apply(
        lambda x: 'red' if x == 30 else 
                ('orange' if x == survey_rank else 'grey')
    )


    # Create the bar chart
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Rank:O', sort='ascending'),
        y='Total Daily Volume (Veh):Q',
        color=alt.Color('color:N', scale=alt.Scale(domain=['grey', 'red','orange'], range=['grey', 'red','orange']),
                    legend=alt.Legend(title="", 
                                        values=['orange','red'],
                                        labelExpr="datum.value == 'orange' ? 'Survey Day' : '30th Busiest Day'")
        )
    ).properties(
        height=400
    )
    return chart
def generate_dotplot_data(data):
    # Assuming survey_date is in session state as a string, and is converted to date format
    survey_date = st.session_state.filter["Survey_Date"].strftime('%d/%m/%Y')
    survey_vol = None
    survey_rank = None

    # Ensure that 'survey_date' exists in the data
    if str(survey_date) in data.index:
        survey_vol = data.loc[data.index == str(survey_date)]['Total Daily Volume (Veh)'].iloc[0]
        survey_rank = data.loc[data['Total Daily Volume (Veh)'] == survey_vol]['Rank'].iloc[0]
    data=data.reset_index(drop=False)
   
    # Make sure 'Date' is in the correct datetime format
    data["Date"] = pd.to_datetime(data["Date"], errors='coerce')  # Ensure 'Date' is a datetime object
    
    # Create a new column to differentiate weekdays (purple) and other days (blue)
    data['color'] = data['Weekday'].apply(
        lambda x: 'purple' if x < 5 else 'blue'
    )

    # Create the dot plot (scatter plot) with date on the x-axis and volume on the y-axis
    chart2 = alt.Chart(data).mark_circle(size=100).encode(
        x="Date:T",  # Treat 'Date' as a temporal field
        y=alt.Y('Total Daily Volume (Veh):Q', title="Total Daily Volume (Veh)"),
        color=alt.Color('color:N', scale=alt.Scale(domain=['purple', 'blue'], range=['purple', 'blue']),
                        legend=alt.Legend(title="Day Type", 
                                          labelExpr="datum.value == 'purple' ? 'Weekday' : 'Weekend'")
        ),
        tooltip=["Date:T", 'Total Daily Volume (Veh):Q', 'Rank', 'Weekday']
    ).properties(
        height=400
    )

    return chart2

   
def get_missing_dates(data, filter_on):
    data=data.reset_index(drop=False)
   
    # Make sure 'Date' is in the correct datetime format
    data["Date"] = pd.to_datetime(data["Date"], errors='coerce')  
    # 1. Get all unique dates in the 'Date' column
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')  # Ensure 'Date' is datetime
    unique_dates = set(data['Date'].dt.date)  # Extract just the date part

    # 2. Create the date range from Start_date to End_date
    start_date = datetime.datetime.combine(filter_on.value["Start_date"], datetime.datetime.min.time())
    end_date = datetime.datetime.combine(filter_on.value["End_date"], datetime.datetime.min.time())
    
    # Generate the date range
    all_dates = pd.date_range(start=start_date, end=end_date).date  # Extract the date part from each datetime

    # 3. Find missing dates (those that are in the range but not in the data)
    missing_dates = [date for date in all_dates if date not in unique_dates]

    # 4. Display missing dates in a table (as a dataframe)
    missing_dates_df = pd.DataFrame(missing_dates, columns=["Missing Dates"])
    return missing_dates_df



def intTab2(tab):
    with tab:
        filter_type = st.session_state.get('filters')[1]
        data=retrieve_data_from_db()
        if filter_type == 'Custom':
            filters = st.session_state.get('Detector_group')[0]
            names = [dict_filt['Name'] for dict_filt in filters]
            sites=Get_unique_sites(data,names)
            custom_sites=filters
        else:
            sites=Get_unique_sites(data)
            custom_sites=None
            

        if 'previous_filter' not in st.session_state:
            st.session_state.previous_filter = None

        
        form = FilterClass()
        form.display_filters(sites,"tab2",True) 

        
        if st.session_state.previous_filter != form:
            st.session_state.previous_filter = form  # Update the previous selection
           
            table_1_html,table_2_html,all_data=Get_daily_average(form,data,custom_sites)
            chart=generate_barplot_data(all_data)
            chart2=generate_dotplot_data(all_data)
            missing_dates = get_missing_dates(all_data, form)
            col1, col2 = st.columns(2)
            
            with col1:
                st.altair_chart(chart2)
                st.markdown(table_1_html, unsafe_allow_html=True)
                
                st.title("Missing Data")
                st.text("All missing dates (from what was imported) between selected start and end date")
                st.dataframe(missing_dates)
                
           
            with col2:
                st.altair_chart(chart)
                st.markdown(table_2_html, unsafe_allow_html=True)
                st.title("Ranked Data")
                st.dataframe(all_data[["Total Daily Volume (Veh)","Rank"]])
                
               
            
                
            
            
        else:
            st.write(f"Selection remains the same: {form}")





        