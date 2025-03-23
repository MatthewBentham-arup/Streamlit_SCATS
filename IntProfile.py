import streamlit as st
import pandas as pd
from filters import FilterClass
from Db_functions import retrieve_data_from_db
import altair as alt
from Intersection_map import Generate_map
import datetime
'''
Int Profile: 
This script is used for all functions pertaining to the Intersection Profiling tab

'''

# HELPER FUNCTIONS -----------------------------------------------------------------
def Aggregate_by_reference(df, reference, exclude_columns=[],aggtype="sum"):
    '''
    Simple Method for joining rows that share the same reference value - used to get total daily volumes in data
    '''
    numeric_columns = df.select_dtypes(include=['number']).columns

    numeric_columns_to_sum = [col for col in numeric_columns if col not in exclude_columns]
    
    grouped = df.groupby(reference).agg(
        {col: aggtype for col in numeric_columns_to_sum} 
    )

    # make sure to keep 'Days of data' columns without summing
    for col in exclude_columns:
        grouped[col] = df.groupby(reference)[col].last()  

    return grouped


def Rolling_volume_calc(df, exclude_columns,rolling_vol):

    """
    Method used to generate rolling volume values by joining 15-minute interval data by columns
    """

    no_of_additional_cols = int(rolling_vol/15 )

  
    # Get all columns in the dataframe
    all_columns = df.columns
    
    # Filter out the columns that should be excluded from the sum
    columns_to_process = [col for col in all_columns if col not in exclude_columns]
    
    # Create a copy of the dataframe to avoid modifying the original dataframe
    df_copy = df.copy()

    
    for i, col in enumerate(columns_to_process):
        if i+no_of_additional_cols > len(columns_to_process):
            df_copy[col]=0
        else:
           
            cols_to_sum = columns_to_process[i:i+no_of_additional_cols] 
            df_copy[col] = df_copy[cols_to_sum].sum(axis=1)

    return df_copy

def Summary_rows(df):
    """
    Method used for calculating Weekend , Weekday and 7 Day averages
    """
    # List of columns that should be summed instead of averaged.
    sum_columns = ['Days of data']

    # Helper function: for a given subset of rows, compute a summary row
    # where each column is aggregated by:
    # - summing if the column is in `sum_columns`
    # - averaging otherwise.
    def summary_row(sub_df, sum_columns):
        summary = {}
        for col in sub_df.columns:
            if col == 'Weekday Name':
                continue
            if col in sum_columns:
                summary[col] = sub_df[col].sum()
            else:
                summary[col] = sub_df[col].mean()
        return summary

    # Define masks for weekdays and weekends.
    weekday_mask = df['Weekday Name'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    weekend_mask = df['Weekday Name'].isin(['Saturday', 'Sunday'])

    # Compute summary rows for each group.
    avg_weekday = summary_row(df.loc[weekday_mask], sum_columns)
    avg_weekday['Weekday Name'] = 'Average Weekday'

    avg_weekend = summary_row(df.loc[weekend_mask], sum_columns)
    avg_weekend['Weekday Name'] = 'Average Weekend'

    avg_7day = summary_row(df, sum_columns)
    avg_7day['Weekday Name'] = 'Average 7 Day'

    # Convert the summary dictionaries to a DataFrame.
    df_summary = pd.DataFrame([avg_7day, avg_weekday, avg_weekend])

    # Reorder the columns to match the original DataFrame.
    df_summary = df_summary[df.columns]

    # Append the new summary rows to the original DataFrame.
    df = pd.concat([df, df_summary], ignore_index=True)
    return df

def calculate_peaks(data):
    '''
    Method Used to get Peak Period and Peak Values in data (hourly)
    '''
    
    
    am_peak_cols = data.columns[:48]  # AM: 0:00 to 11:45 (0-47)
    pm_peak_cols = data.columns[48:95]  # PM: 12:00 to 23:45 (48-95)

    # Function to get the column with max value for a peak period
    def get_max_peak_column(row, peak_cols):
        max_val_col = row[peak_cols].idxmax()  
        return max_val_col

    # Apply to each row and create new columns
    data['AM_peak_max'] = data.apply(lambda row: get_max_peak_column(row, am_peak_cols), axis=1)
    data['PM_peak_max'] = data.apply(lambda row: get_max_peak_column(row, pm_peak_cols), axis=1)
    data['AM_peak_max_val'] = data.apply(lambda row: row[row['AM_peak_max']], axis=1)
    data['PM_peak_max_val'] = data.apply(lambda row: row[row['PM_peak_max']], axis=1)

    return data

def get_days_of_data(data):
    '''
    Function to get Days of data in a given aggregated row
    '''
    data['Days of data']=data['Weekday'].map(data.groupby('Weekday').count()['Year'].to_dict())
    return data

def Get_unique_sites(data,custom=None):
    '''
    Method to get list of unique sites and in cases of custom filtering 
    '''
    sites=data['NB_SCATS_SITE'].unique().tolist()
    sites.append('ALL SITES')
    if custom:
        for name in custom:
            sites.append(name)
    return sites


def transform_table(orig_df,rolling_int):
    '''
    Method for converting data into HTML table (for nice looking table - dont hate!)
    '''

    # 1. Rename Columns
    new_df = pd.DataFrame({
    "Average volumes": orig_df["Weekday Name"],
    "AM Peak period (start)": orig_df["AM_peak_max"],
    "AM Volume": orig_df["AM_peak_max_val"],
    "PM Peak period (start)": orig_df["PM_peak_max"],
    "PM Volume": orig_df["PM_peak_max_val"],   
    "Daily Average": orig_df['QT_VOLUME_24HOUR'],          
    "Days of data": orig_df["Days of data"]
})
    # MULTIINDEX COLUMNS - this is needed to have the merged cells header looks
    columns = pd.MultiIndex.from_tuples([
        ("", "Average volumes"),
        ("AM", "Peak period (start)"),
        ("AM", "Volume"),
        ("PM", "Peak period (start)"),
        ("PM", "Volume"),
        ("", "Daily Average"),
        ("", "Days of data")
    ])

    new_df.columns = columns
    new_df = new_df.round(0)
    numeric_columns = new_df.select_dtypes(include=['float64']).columns
    new_df[numeric_columns] = new_df[numeric_columns].astype('int')


    # Build the HTML table string with merged headers
    html_table = f"""
    <div class="card tab" style="grid-row: 2; grid-column: 1;">
    <div class="charts-card card-inner table-container">
        <table id="summary" border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr>
            <th colspan="7">Site Summary - Peak volumes represent {rolling_int} min volumes</th>
            </tr>
            <tr>
            <th rowspan="2">Average volumes</th>
            <th colspan="2">AM</th>
            <th colspan="2">PM</th>
            <th rowspan="2">Daily Average</th>
            <th rowspan="2">Days of data</th>
            </tr>
            <tr>
            <th>Peak period (start)</th>
            <th>Volume</th>
            <th>Peak period (start)</th>
            <th>Volume</th>
            </tr>
        </thead>
        <tbody>
    """

    # Fill in the table rows using the values in new_df
    for idx, row in new_df.iterrows():
        html_table += "        <tr>\n"
        for col in new_df.columns:
            html_table += f"          <td>{row[col]}</td>\n"
        html_table += "        </tr>\n"

    # Close the table tags
    html_table += """      </tbody>
        </table>
    </div>
    </div>
    """
    return html_table
   
    



def Scats_data_analysis(filter_on,data,custom_sites,all_sites,col1):
    '''
    This is the main function which filters and aggregates the data into average rolling values 
    '''
    
    # 1 Site Filtering ---------------------------------------------------------------------------
    exclude_in_sum=["Month","NB_SCATS_SITE","NB_DETECTOR","Weekday","Year","QT_INTERVAL_COUNT"]
    site_filter = filter_on.value["Site_no"]

    if type(site_filter) is int: # CASE 1: Single site is chossen
        filtered_data = data.loc[data['NB_SCATS_SITE']==site_filter]
    elif site_filter== "ALL SITES":# CASE 2: all sites are chossen - no filtering needed
        filtered_data=data
    elif custom_sites:# CASE 3: Custom Site is choseen

        filt_dict =  next((d for d in custom_sites if d["Name"] == site_filter),None)
        site_filters = filt_dict["Sites"]
        filter_query = False  

        for site_filt in site_filters:
            site_f = site_filt["Site"]
            detects = site_filt["Detectors"]
            filter_query |= (data['NB_SCATS_SITE'] == site_f) & (data['NB_DETECTOR'].isin(detects))

        filtered_data = data.loc[filter_query]


    # Date Filtering ---------------------------------------------------------------------------
    filtered_data["QT_INTERVAL_COUNT"] = pd.to_datetime(filtered_data["QT_INTERVAL_COUNT"])
    
    is_between_dates = (filtered_data["QT_INTERVAL_COUNT"] > datetime.datetime.combine(filter_on.value["Start_date"], datetime.datetime.min.time())) & (filtered_data["QT_INTERVAL_COUNT"] < datetime.datetime.combine(filter_on.value["End_date"], datetime.datetime.min.time()) )
    filtered_data=filtered_data.loc[is_between_dates]
 
    if filtered_data.empty:
        with col1:
            st.error("No data matching filters (remember to check dates used).If this is a custom filter please ensure the sites and detectors exists in the data you have inputted.")
            exit()
    else:
        
        # GENERATE MAP WITH CHOSSEN SITES ----------------------------------------------------------
        Generate_map(site_filter,all_sites,custom_sites,col1,14)


        # DATA WRANGLING --------------------------------------------------------------------------
       
        #1. GET Rolling Volume ----------------------------------------------------------------------------
        rolling_int= filter_on.value["Rolling_vol"]
    
        exclude_in_rol=["Reference","Month","NB_SCATS_SITE","NB_DETECTOR","Weekday","Year","QT_INTERVAL_COUNT","NM_REGION","CT_RECORDS","QT_VOLUME_24HOUR","CT_ALARM_24HOUR"]
        aggregated_data=Rolling_volume_calc(filtered_data,exclude_in_rol,rolling_int)

        #2. Group by date ---------------------------------------------------------------------------
        aggregated_data=Aggregate_by_reference(aggregated_data,"Reference",exclude_in_sum,"sum")
    
        aggregated_data=get_days_of_data(aggregated_data)\

        #3. Group by Daytype ---------------------------------------------------------------------------
        aggregated_data=Aggregate_by_reference(aggregated_data,"Weekday",exclude_in_sum,"mean")
        
        #Drop unnessary columns ---------------------------------------------------------------------
        aggregated_data=aggregated_data.drop(['Year',"QT_INTERVAL_COUNT","CT_ALARM_24HOUR","Month","CT_RECORDS","NB_SCATS_SITE","NB_DETECTOR"],axis=1)
        weekday_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

        #4. Add Summary rows -------------------------------------------------------------------------
        aggregated_data['Weekday Name'] = aggregated_data['Weekday'].map(weekday_map)
        aggregated_data=Summary_rows(aggregated_data)
        #5. Add Peaks -------------------------------------------------------------------------
        aggregated_data=calculate_peaks(aggregated_data)
        #6. transform table to make it look nice------------------------------------------------------------------------------
        tabled_data=transform_table(aggregated_data,rolling_int)

        return tabled_data,aggregated_data
       

#-------------------------------------------

# LINE PLOT CODE

#--------------------------------------------
def pivot_table(data):
    cols_to_exclude =["Days of data","Weekday","Weekday Name","AM_peak_max",
    "PM_peak_max","AM_peak_max_val","PM_peak_max_val","QT_VOLUME_24HOUR"]

    pivot_cols = data.columns[~data.columns.isin(cols_to_exclude)].tolist()
    data_long = pd.melt(data, 
                    id_vars=cols_to_exclude,  
                    value_vars=pivot_cols, 
                    var_name='Time (mm:ss)', 
                    value_name='Rolling Volume (veh)') 
    return data_long

def generate_lineplot_data(data):
    '''
    Method for generating the 
    '''
    
    data_long = pivot_table(data)
   
    data_long['Time (mm-ss)'] = pd.to_datetime(data_long['Time (mm:ss)'], format='%M:%S')
    data_long['strokeDash'] = data_long['Weekday Name'].apply(
    lambda x: True if 'averag' in x.lower() else False
)
    # Define custom order for 'Weekday Name' to sort by weekday order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Average 7 Day','Average Weekday','Average Weekend']

    # Convert 'Weekday Name' column to categorical type with the custom order
    data_long['Weekday Name'] = pd.Categorical(data_long['Weekday Name'], categories=weekday_order, ordered=True)
    data_long=data_long.sort_values("Weekday")
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Average 7 Day','Average Weekday','Average Weekend']
    nearest = alt.selection_point(nearest=True, on="pointerover",
                    fields=['Time (mm-ss)','Rolling Volume (veh)'], empty=False)
    
    lines = alt.Chart(data_long).mark_line().encode(
        x=alt.X('Time (mm-ss):T').axis(format='%M:%S'),  # Use the proper time format
        y='Rolling Volume (veh):Q',
        strokeDash=alt.StrokeDash('strokeDash:N', legend=None),
        color=alt.Color('Weekday Name:N', scale=alt.Scale( range=['#D60093', '#800080', '#FF9933', '#00B050','#00B0F0','#4472C4','#264478','#404040','#C00000','#5B9BD5']),sort=weekday_order)
    )
    when_near = alt.when(nearest)
    # Draw points on the line, and highlight based on selection
    points = lines.mark_point().encode(
        opacity=when_near.then(alt.value(1)).otherwise(alt.value(0))
    )
    
    # Draw a rule at the location of the selection
    rules = alt.Chart(data_long).transform_pivot(
    "Weekday Name",
    value="Rolling Volume (veh)",
    groupby=["Time (mm-ss)"]).mark_rule(color="gray").encode(
    x=alt.X('Time (mm-ss):T').axis(format='%M:%S'),
    opacity=when_near.then(alt.value(0.3)).otherwise(alt.value(0)),
   tooltip=[ 
        alt.Tooltip(c, type="quantitative", format=".0f")  # .0f formats numbers as integers (no decimals)
        for c in weekday_order
    ],).add_params(nearest)

    # Put the five layers into a chart and bind the data
    chart=alt.layer(
        lines, points, rules
    ).properties(
        height=500,
         title=f'Daily Traffic Profile ({ str(st.session_state.filter["Site_no"]).title()})  '
    )

    return chart
    



def adjust_dataframe(data):

    # Rename Columns:
    data=data.rename({'AM_peak_max':'Peak Period (AM)','PM_peak_max':'Peak Period (PM)','AM_peak_max_val':'Peak Volume (AM)','PM_peak_max_val':'Peak Volume (PM)'},axis=1)
    data=data.drop(columns ="Weekday")

    # Edit Column Orders and Change Index
    cols_to_move = data.columns[-6:].tolist() 
    remaining_cols = data.columns[:-6].tolist() 
    new_column_order = cols_to_move + remaining_cols 
    edited_data = data[new_column_order].set_index('Weekday Name')

    return edited_data 

def intTab(tab):

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

        data["QT_INTERVAL_COUNT"] = pd.to_datetime(data["QT_INTERVAL_COUNT"])
        max_date = data["QT_INTERVAL_COUNT"].max()
        min_date = data["QT_INTERVAL_COUNT"].min()
        
        form = FilterClass()
        
        col1, map_col= st.columns([1,4])
        graph_col,col2= st.columns([3,2])
        with col1:
            form.display_filters(sites,"tab1",max_date,min_date) 
        
        
        if st.session_state.previous_filter != form:
            st.session_state.previous_filter = form  # Update the previous selection
           
            tabled_data,all_data=Scats_data_analysis(form,data,custom_sites,sites,map_col)
            chart=generate_lineplot_data(all_data)
            
            
          
            with graph_col:
            
                st.altair_chart(chart,key='Rounded')
             
            with col2:
                st.markdown(tabled_data, unsafe_allow_html=True)
            
            st.title("Aggregated Data")
            

            edited_data=adjust_dataframe(all_data)
            st.dataframe(edited_data)
            
            
        else:
            st.write(f"Selection remains the same: {form}")





        