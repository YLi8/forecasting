import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import os

st.header('5-Year Data of 3 Areas in PJM')
st.write('By Yun Li')
markdown_text = '''
The data are collected from the [PJM’s Data Miner 2] (https://dataminer2.pjm.com).
The solar data are not available before 2019, synthetic data from [PVWatts] (https://pvwatts.nrel.gov) are used. 
Given an address (city name or zip code), 
PVWatts calculates the electricity production of a PV system using an hour-by-hour simulation over one year. 
The temperature data are collected from [NOAA] (https://www.noaa.gov/). 
The 3 selected areas are MIDATL, SOUTH, and WEST.
Data from 01/01/2015 to 12/31/2018 are used for training, and data from 01/01/2019 to 12/31/2019 are used for testing.
'''
st.markdown(markdown_text)


@st.cache
def load_data():
    DATA_PATH = os.path.join( "data/l1")
    df = pd.DataFrame(columns=[ "Location", "Year", "Month", "Day", "Weekday", "Hour","Demand", "Temperature"])
    for root, dirs, files in os.walk(DATA_PATH):
        date = pd.read_csv(os.path.join(root, "Date.csv"))
        month_series = date["Month"]
        curr_year = 2015
        year_series = [0 for i in month_series]
        
        for i in range(len(month_series)-1):
            if month_series[i+1] >= month_series[i]:
                year_series[i] += curr_year
            else:
                year_series[i] += curr_year
                curr_year+=1

        year_series[-1] += curr_year
        
        for file in files:
            if file != "Date.csv" and file != "fcst.csv" and file != "test.csv":
                t = pd.read_csv(os.path.join(root, file))
                if "Demand" in t.columns:
                    temp_df = pd.DataFrame(data = t["Demand"])
                else:
                    temp_df = pd.DataFrame(data = t["Net"])
                    temp_df["Demand"] = temp_df["Net"]
                    temp_df.drop(columns=["Net"], inplace = True)
                
                temp_df["Location"] = file.split(".")[0]
                temp_df["Year"] = year_series
                temp_df["Month"] = month_series
                temp_df["Day"] = date["Day"]
                temp_df["Hour"] = date["Hour"]
                temp_df["Weekday"] = date["Weekday"]
                temp_df["Temperature"] = t["Temperature"]
                
                df = pd.concat([df, temp_df])
    
    df['DateTime'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour']])                
    df = df.set_index('DateTime')                
    df.rename(columns={'Demand': 'Load'}, inplace=True)       
    df_daily = df.groupby(['Location'])[['Load']].resample('D').mean().reset_index(level=['Location'])   
    locations = df.Location.unique()
    
    return df, df_daily, locations


df, df_daily, locations = load_data()



st.subheader('Time Series of Load')


load_ts_res = st.radio('load_ts_res', ['Daily', 'Hourly'], horizontal=True, label_visibility='collapsed')

if load_ts_res == 'Hourly':
    fig = px.line(df, x=df.index, y='Load', color='Location')
else:
    fig = px.line(df_daily, x=df_daily.index, y='Load', color='Location')
fig.update_layout(margin={'t': 50},xaxis_title="Datetime",yaxis_title = "Load (kW)")
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label='1 month', step='month', stepmode='backward'),
            dict(count=3, label='3 months', step='month', stepmode='backward'),
            dict(count=6, label='6 months', step='month', stepmode='backward'),
            dict(count=12, label='1 year', step='month', stepmode='backward'),
            dict(step='all')
        ])
    )
)


st.plotly_chart(fig)



st.subheader('Summary Statistics of Load')


load_stat_res = st.radio('load_stat_res', ['By month', 'By hour'], horizontal=True, label_visibility='collapsed')

if load_stat_res == 'By hour':     
    fig = px.box(df, x='Hour', y='Load', color='Location', labels={'Load': 'Load (kW)'})
else:
    fig = px.box(df, x='Month', y='Load', color='Location', labels={'Load': 'Load (kW)'})
fig.update_layout(margin={'t': 30}, boxmode='group',xaxis_title="Datetime",yaxis_title = "Load (kW)")


st.plotly_chart(fig)



st.subheader('Correlation Analysis')


load_temp_res = st.radio('load_temp_res', ['By month', 'By hour'], horizontal=True, label_visibility='collapsed')

if load_temp_res == 'By hour':
    fig = px.scatter(
        df, x='Temperature', y='Load', color='Location',
        facet_col='Hour', facet_col_wrap=6, facet_row_spacing=0.03, height=900,
        labels={'Temperature': 'T (\u00b0C)', 'Load': 'Load (kW)'},
        category_orders={'Hour': list(range(24))}
    )
else:
    fig = px.scatter(
        df, x='Temperature', y='Load', color='Location',  facet_col='Month', facet_col_wrap=6, height=500,
        labels={'Temperature': 'Temperature (\u00b0C)', 'Load': 'Load (kW)'}
    )
fig.update_layout(margin={'t': 30})

st.plotly_chart(fig)















