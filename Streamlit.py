import streamlit as st
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load the data
df=pd.read_csv("Data.csv")
col1,col2=st.columns(2)
with col1:
    st.title('ROAD ACCIDENT DASHBOARD')
    st.header('Accident Severity Distribution')
with col2:
    st.image('aci2.jpeg')
# Display a colorful divider
# Display a colorful divider
st.markdown("""<div style="height: 2px; background-color: #fca311; margin: 15px 0;"></div>""", unsafe_allow_html=True)


#Slicer
# Add a tab inside the sidebar
with st.sidebar.expander("Filter Options", expanded=True):
    # Sidebar: Urban or Rural selection
    urban_rural_options = ['All', 'Urban', 'Rural']  # Include "All" option
    selected_urban_rural = st.selectbox("Select Urban/Rural", urban_rural_options)

    # Sidebar: Year selection
    selected_year = st.selectbox("Select Year", ["All"] + df['Year'].unique().tolist())

# Filter the data based on the selected urban/rural area and year
if selected_urban_rural == "All":
    filtered_df = df  # No filtering for "All" option
else:
    filtered_df = df[df['Urban_or_Rural_Area'] == selected_urban_rural]

if selected_year != "All":
    filtered_df = filtered_df[filtered_df['Year'] == selected_year]
st.divider()
col1,col2=st.columns(2)
with col1:
    st.image('accident.jpeg')
with col2:
    # Replace 'Taxi/Private hire car' with 'Car' in the 'Vehicle_Type' column
    df['Vehicle_Type'].replace({'Taxi/Private hire car': 'Car'}, inplace=True)
    df['Vehicle_Type'].replace({'Bus or coach (17 or more pass seats)': 'Bus', 'Minibus (8 - 16 passenger seats)': 'Bus'}, inplace=True)
    df['Vehicle_Type'].replace({
    'Van / Goods 3.5 tonnes mgw or under': 'Van',
    'Goods over 3.5t. and under 7.5t': 'Van',
    'Goods 7.5 tonnes mgw and over': 'Van'
}, inplace=True)
    df['Vehicle_Type'] = df['Vehicle_Type'].replace({
    'Motorcycle 125cc and under': 'Motorcycle',
    'Motorcycle 50cc and under': 'Motorcycle',
    'Motorcycle over 125cc and up to 500cc': 'Motorcycle',
    'Motorcycle over 500cc': 'Motorcycle'
})
    df['Vehicle_Type'].replace({
    'Motorcycle 125cc and under': 'Bike',
    'Motorcycle 50cc and under': 'Bike',
    'Motorcycle over 125cc and up to 500cc': 'Bike',
    'Motorcycle over 500cc': 'Bike'
}, inplace=True)
    df['Vehicle_Type'].replace({
    'Other vehicle': 'Other',
    'Pedal cycle': 'Other',
    'Ridden horse': 'Other'
}, inplace=True)
    
    if selected_year == "All":
        if selected_urban_rural == "All":
            filtered_df = df  # No filtering needed for "All" option in both year and area
        else:
            filtered_df = df[df['Urban_or_Rural_Area'] == selected_urban_rural]  # Filter by urban/rural area only
    else:
        if selected_urban_rural == "All":
            filtered_df = df[df['Year'] == selected_year]  # Filter by year only
        else:
            filtered_df = df[(df['Year'] == selected_year) & (df['Urban_or_Rural_Area'] == selected_urban_rural)]  # Filter by both year and urban/rural area
            
    casualties_by_vehicle = filtered_df.groupby('Vehicle_Type')['Number_of_Casualties'].sum().reset_index()
    vehicle_symbols = {
    'Car': '🚗',
    'Bicycle': '🚲',
    'Bus': '🚌',
    'Motorcycle': '🏍️',
    'Truck': '🚚',
    'Van': '🚐',
    'Other': '🚕',  # Assigning a generic symbol for "Other"
    'Agricultural vehicle': '🚜'
}


    st.write("Sum of Casualties by Vehicle")
    st.write(casualties_by_vehicle)


st.divider()

# Replace 'Bus or coach (17 or more pass seats)' and 'Minibus (8 - 16 passenger seats)' with 'Bus' in the 'Vehicle_Type' column

# Filter DataFrame based on selected options




#_________________________________________________

#_____________________________________________
#pie chart  
# Group filtered data by Accident Severity and calculate total casualties for each severity category
severity_casualty = filtered_df.groupby('Accident_Severity')['Number_of_Casualties'].sum().reset_index()

# Plot the pie chart using Plotly
fig = px.pie(severity_casualty, values='Number_of_Casualties', names='Accident_Severity', 
             title='Accident Severity Distribution Based on Number of Casualties')

# Display the chart
st.plotly_chart(fig)
st.divider()
#___________________________________________
#line chart
# Group data by year and month and calculate the total number of casualties
casualty_trend = filtered_df.groupby(['Year', 'Month'])['Number_of_Casualties'].sum().reset_index()

# Define the order of the months
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Pivot the data to have months as columns and years as separate columns
pivot_table = casualty_trend.pivot(index='Month', columns='Year', values='Number_of_Casualties')

# Reorder the rows based on the custom month order
pivot_table = pivot_table.reindex(month_order)

# Plot the line chart
fig = px.line(pivot_table, x=pivot_table.index, y=pivot_table.columns, title=f"Casualty Trends Over Time ({selected_urban_rural})")
fig.update_layout(xaxis_title='Month', yaxis_title='Total Number of Casualties', legend_title='Year')

# Set y-axis range and tick marks
fig.update_yaxes(range=[0, pivot_table.max().max() + 5000], tickmode='linear', tick0=0, dtick=5000, showgrid=True)

# Display the line chart
st.plotly_chart(fig)
st.divider()
#_______________________
#bar of week
# Define the order of the days of the week
day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

# Group data by day of the week and calculate the total number of casualties
day_of_week_casualties = filtered_df.groupby('Day_of_Week')['Number_of_Casualties'].sum().reindex(day_order)

# Plot the bar chart
fig = px.bar(day_of_week_casualties, x=day_of_week_casualties.index, y='Number_of_Casualties', 
             title=f"Accident Frequency by Day of the Week ({selected_year}, {selected_urban_rural} Areas)",
             labels={'Number_of_Casualties': 'Total Number of Casualties', 'Day_of_Week': 'Day of the Week'})
fig.update_layout(xaxis_title='Day of the Week', yaxis_title='Total Number of Casualties')

# Display the bar chart
st.plotly_chart(fig)
#______________________________________
st.divider()
#Casualities by vehicle

# Mode imputation for categorical variables
categorical_cols = df.select_dtypes(include=['object']).columns  # Select categorical columns
df[categorical_cols] = df[categorical_cols].fillna(df.mode().iloc[0])  # Fill missing values with mode

# Count missing values for each variable
missing_values_count = df.isna().sum()

# Replace values 'Wet or damp' and 'Flood over 3cm. deep' with 'Wet' in the 'Road_Surface_Conditions' column
df['Road_Surface_Conditions'].replace({'Wet or damp': 'Wet', 'Flood over 3cm. deep': 'Wet'}, inplace=True)

# Replace 'Frost or ice' with 'Snow' in the 'Road_Surface_Conditions' column
df['Road_Surface_Conditions'].replace({'Frost or ice': 'Snow'}, inplace=True)

# Filter DataFrame based on selected options
if selected_urban_rural == "All" and selected_year == "All":
    filtered_df = df.copy()  # Select all data
elif selected_urban_rural == "All":
    filtered_df = df[df['Year'] == selected_year]  # Filter by year only
elif selected_year == "All":
    filtered_df = df[df['Urban_or_Rural_Area'] == selected_urban_rural]  # Filter by urban/rural area only
else:
    filtered_df = df[(df['Urban_or_Rural_Area'] == selected_urban_rural) & (df['Year'] == selected_year)]  # Filter by both

# Group by 'Road_Surface_Conditions' and calculate the sum of 'Number_of_Casualties'
surface_casualty_sum = filtered_df.groupby('Road_Surface_Conditions')['Number_of_Casualties'].sum().reset_index()

# Create treemap
#fig = px.treemap(surface_casualty_sum, path=['Road_Surface_Conditions'], values='Number_of_Casualties')

# Create treemap with title
fig = px.treemap(surface_casualty_sum, 
                 path=['Road_Surface_Conditions'], 
                 values='Number_of_Casualties', 
                 title="Total Casualties by Road Surface")

# Display the treemap
st.plotly_chart(fig)
st.divider()

#_______________________________________


#________________________________
#bar of day dark 
# Group by 'Light_Conditions' and 'Accident_Severity' and calculate the sum of 'Number_of_Casualties'
grouped_df = filtered_df.groupby(['Light_Conditions', 'Accident_Severity'])['Number_of_Casualties'].sum().reset_index()

# Replace the values on the x-axis with the modified values
grouped_df['Light_Conditions'].replace({'Darkness - lights lit': 'Darkness',
                                        'Darkness - lighting unknown': 'Darkness',
                                        'Darkness - lights unlit': 'Darkness',
                                        'Darkness - no lighting': 'Darkness'}, inplace=True)

# Plot the bar chart
fig = px.bar(grouped_df, 
             x='Light_Conditions', 
             y='Number_of_Casualties', 
             color='Accident_Severity', 
             barmode='group', 
             labels={'Number_of_Casualties': 'Total Casualties'},
             title='Total Casualties by Light Conditions and Accident Severity')

# Show the chart
st.plotly_chart(fig)
st.divider()
#___________________________________

# Group by 'Road_Type' and calculate the sum of 'Number_of_Casualties'
road_type_casualty_sum = filtered_df.groupby('Road_Type')['Number_of_Casualties'].sum().reset_index()

# Sort the DataFrame by 'Number_of_Casualties' in descending order
road_type_casualty_sum = road_type_casualty_sum.sort_values(by='Number_of_Casualties', ascending=True)

# Plot the horizontal bar chart
fig = px.bar(road_type_casualty_sum, 
             x='Number_of_Casualties', 
             y='Road_Type', 
             labels={'Number_of_Casualties': 'Total Casualties'},
             title='Total Casualties by Road Type',
             orientation='h')

# Show the chart
st.plotly_chart(fig)
st.divider()
