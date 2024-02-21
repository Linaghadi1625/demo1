import streamlit as st
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load the data
df=pd.read_csv("Data.csv")
# Sidebar
st.sidebar.title("Filters")
selected_tab = st.sidebar.radio("Select Tab", ["Data", "Charts"])

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

# Main content
if selected_tab == "Data":
    st.write("The dataset provides detailed information about road accidents, including when and where they happened, how severe they were, and how many people and vehicles were involved. It also includes details like road conditions, weather, and whether the accidents occurred in urban or rural areas. This data helps us understand accident patterns and risks better, which can be used by policymakers and others to make roads safer.")

    st.image("accidentt.jpg", width=400)

    st.write(f"Selected Urban/Rural Area: {selected_urban_rural}")
    st.write(f"Selected Year: {selected_year}")
    st.write(filtered_df)  # Display filtered DataFrame

    st.subheader("Please select an ID :")
    
    # Filter suggestions based on search term
    suggestion_options = filtered_df['Accident_Index'].unique().tolist()

    # Display selectbox with filtered suggestions
    selected_suggestion = st.selectbox("Select Accident Index:", [""] + suggestion_options)

    if selected_suggestion:
        search_term = selected_suggestion

        # Perform VLOOKUP-like operation
        result_df = filtered_df[filtered_df['Accident_Index'] == search_term]
        if not result_df.empty:
            st.write("Matching Rows:")
            st.write(result_df)
        else:
            st.write("No matching rows found.")


else:
    st.header("Charts")

    # Visualization 1: Pie Chart - Accident Severity Distribution Based on Number of Casualties
    severity_casualty = filtered_df.groupby('Accident_Severity')['Number_of_Casualties'].sum().reset_index()
    if 'severity_casualty' in locals():
        fig = px.pie(severity_casualty, values='Number_of_Casualties', names='Accident_Severity', 
                     title='Accident Severity Distribution Based on Number of Casualties', hole=0.5)  # Set the size of the hole to make it look like a donut chart
    st.plotly_chart(fig)

    # Divider
    st.divider()

    # Visualization 2: Bar Chart - Total Casualties by Vehicle Type
    def standardize_vehicle_types(df):
        vehicle_mappings = {
            'Taxi/Private hire car': 'Car',
            'Bus or coach (17 or more pass seats)': 'Bus',
            'Minibus (8 - 16 passenger seats)': 'Bus',
            'Van / Goods 3.5 tonnes mgw or under': 'Van',
            'Goods over 3.5t. and under 7.5t': 'Van',
            'Goods 7.5 tonnes mgw and over': 'Van',
            'Motorcycle 125cc and under': 'Motorcycle',
            'Motorcycle 50cc and under': 'Motorcycle',
            'Motorcycle over 125cc and up to 500cc': 'Motorcycle',
            'Motorcycle over 500cc': 'Motorcycle',
            'Pedal cycle': 'Other',
            'Other vehicle': 'Other',
            'Ridden horse': 'Other'
        }
        df['Vehicle_Type'].replace(vehicle_mappings, inplace=True)
        return df

    def filter_data(df, selected_year, selected_urban_rural):
        filtered_df = df.copy()
        if selected_year != "All":
            filtered_df = filtered_df[filtered_df['Year'] == selected_year]
        if selected_urban_rural != "All":
            filtered_df = filtered_df[filtered_df['Urban_or_Rural_Area'] == selected_urban_rural]
        return filtered_df

    df = standardize_vehicle_types(df)
    filtered_df = filter_data(df, selected_year, selected_urban_rural)

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

    def add_symbols(row):
        if row['Vehicle_Type'] in vehicle_symbols:
            return f"{vehicle_symbols[row['Vehicle_Type']]} {row['Vehicle_Type']}"
        else:
            return row['Vehicle_Type']

    casualties_by_vehicle['Vehicle_Type'] = casualties_by_vehicle.apply(add_symbols, axis=1)

    st.write("Sum of Casualties by Vehicle")
    st.write(casualties_by_vehicle)

    # Divider
    st.divider()

    # Visualization 3: Line Chart - Casualty Trends Over Time
    casualty_trend = filtered_df.groupby(['Year', 'Month'])['Number_of_Casualties'].sum().reset_index()
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_table = casualty_trend.pivot(index='Month', columns='Year', values='Number_of_Casualties')
    pivot_table = pivot_table.reindex(month_order)
    fig = px.line(pivot_table, x=pivot_table.index, y=pivot_table.columns, title=f"Casualty Trends Over Time ({selected_urban_rural})")
    fig.update_layout(xaxis_title='Month', yaxis_title='Total Number of Casualties', legend_title='Year')
    fig.update_yaxes(range=[0, pivot_table.max().max() + 5000], tickmode='linear', tick0=0, dtick=5000, showgrid=True)
    st.plotly_chart(fig)

    # Divider
    st.divider()

    # Visualization 4: Bar Chart - Accident Frequency by Day of the Week
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_of_week_casualties = filtered_df.groupby('Day_of_Week')['Number_of_Casualties'].sum().reindex(day_order)
    fig = px.bar(day_of_week_casualties, x=day_of_week_casualties.index, y='Number_of_Casualties', 
                 title='Accident Frequency by Day of the Week',
                 labels={'Number_of_Casualties': 'Total Casualties', 'Day_of_Week': 'Day of the Week'})
    st.plotly_chart(fig, use_container_width=True)

    # Divider
    st.divider()

    # Visualization 5: Treemap - Total Casualties by Road Surface Conditions
    categorical_cols = df.select_dtypes(include=['object']).columns  
    df[categorical_cols] = df[categorical_cols].fillna(df.mode().iloc[0])  
    df['Road_Surface_Conditions'].replace({'Wet or damp': 'Wet', 'Flood over 3cm. deep': 'Wet'}, inplace=True)
    df['Road_Surface_Conditions'].replace({'Frost or ice': 'Snow'}, inplace=True)
    if selected_urban_rural == "All" and selected_year == "All":
        filtered_df = df.copy()  
    elif selected_urban_rural == "All":
        filtered_df = df[df['Year'] == selected_year]  
    elif selected_year == "All":
        filtered_df = df[df['Urban_or_Rural_Area'] == selected_urban_rural]  
    else:
        filtered_df = df[(df['Urban_or_Rural_Area'] == selected_urban_rural) & (df['Year'] == selected_year)]  
    surface_casualty_sum = filtered_df.groupby('Road_Surface_Conditions')['Number_of_Casualties'].sum().reset_index()
    fig = px.treemap(surface_casualty_sum, path=['Road_Surface_Conditions'], values='Number_of_Casualties',title="Total Casualties by Road Surface Conditions")
    st.plotly_chart(fig)

    # Divider
    st.divider()

    # Visualization 6: Bar Chart - Total Casualties by Light Conditions and Accident Severity
    grouped_df = filtered_df.groupby(['Light_Conditions', 'Accident_Severity'])['Number_of_Casualties'].sum().reset_index()
    grouped_df['Light_Conditions'].replace({'Darkness - lights lit': 'Darkness', 'Darkness - lighting unknown': 'Darkness',
                                            'Darkness - lights unlit': 'Darkness', 'Darkness - no lighting': 'Darkness'},
                                           inplace=True)
    fig = px.bar(grouped_df, x='Light_Conditions', y='Number_of_Casualties', color='Accident_Severity',
                 title='Total Casualties by Light Conditions and Accident Severity',
                 labels={'Number_of_Casualties': 'Total Casualties', 'Light_Conditions': 'Light Conditions'})
    st.plotly_chart(fig, use_container_width=True)

    # Divider
    st.divider()

    # Visualization 7: Bar Chart - Total Casualties by Road Type
    road_type_casualty_sum = filtered_df.groupby('Road_Type')['Number_of_Casualties'].sum().reset_index()
    road_type_casualty_sum = road_type_casualty_sum.sort_values(by='Number_of_Casualties', ascending=True)
    fig = px.bar(road_type_casualty_sum, 
                 x='Number_of_Casualties', 
                 y='Road_Type', 
                 labels={'Number_of_Casualties': 'Total Casualties'},
                 title='Total Casualties by Road Type',
                 orientation='h')
    st.plotly_chart(fig)

    # Divider
    st.divider()

    # Visualization 8: Bar Chart - Total Casualties by Junction Detail
    junction_casualties = filtered_df.groupby('Junction_Detail')['Number_of_Casualties'].sum().reset_index()
    fig = px.bar(junction_casualties, x='Junction_Detail', y='Number_of_Casualties', 
                 title='Total Casualties by Junction Detail', labels={'Number_of_Casualties': 'Total Casualties'})
    st.plotly_chart(fig, use_container_width=True)

    # Divider
    st.divider()

    # Visualization 9: Bar Chart - Sum of Casualties by Speed Limit
    speed_limit_casualties = filtered_df.groupby('Speed_limit')['Number_of_Casualties'].sum().reset_index()
    fig = px.bar(speed_limit_casualties, x='Speed_limit', y='Number_of_Casualties', 
                 title='Sum of Casualties by Speed Limit', labels={'Number_of_Casualties': 'Sum of Casualties'})
    st.plotly_chart(fig, use_container_width=True)
