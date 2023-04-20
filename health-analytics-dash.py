# -*- coding: utf-8 -*-
"""
Created on Monday November 7th 2022

@author: joshiggins
"""
# Importing full packages
import geopy
import openpyxl
import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import leafmap.foliumap as leafmap
import pyodbc

# Importing partial packages
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

# Defining database connection
# conn = pyodbc.connect('Driver={SQL Server};' 'Server=hackathon.spdns.org;' 'Database=GlobalHealth;' 'Trusted_Connection=no;' 'uid=ServiceStreamlit;' 'pwd=Hack1234;')
# health_analytics_query = 'SELECT * FROM Data.HealthAnalytics'
# health_df = pd.read_sql(health_analytics_query, conn)

st.set_page_config(page_title='TIPAC',  layout='wide', page_icon=':hospital:')

# this is the header
t1, t2 = st.columns((0.07,1)) 

t1.image('images/index.png', width = 120)
t2.title("Tool for Integrated Planning and Costing")
# t2.markdown("TIPAC")

tab1, tab2 = st.tabs(["Financing", "Disease"])

with tab1:

    with st.spinner('Updating Report...'):
        
        # Filtering to Region
        health_df = pd.read_excel('health-analytics-data.xlsx', sheet_name='regions')
        region_1 = st.selectbox('Choose Region ', health_df, help='Filter report to show only one region')

        # Creating header boxes
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))
        
        # Filling header boxes in
        m1.write('')
        m2.metric(label='Total Current Spend', value = str('$10M'), delta = str('$5M')+' more compared to last month', delta_color = 'inverse')
        # m3.metric(label ='Current Handover Average',value = str(int(ch['Value']))+" Mins", delta = str(int(ch['Previous']))+' Compared to 1 hour ago', delta_color = 'inverse')
        # m4.metric(label = 'Time Lost today (Above 15 mins)',value = str(int(hl['Value']))+" Hours", delta = str(int(hl['Previous']))+' Compared to yesterday')
        m1.write('')

with tab2:

    with st.spinner('Updating Report...'):
        
        # Filtering to Region
        health_df = pd.read_excel('health-analytics-data.xlsx', sheet_name='regions')
        region_2 = st.selectbox('Choose Region', health_df, help='Filter report to show only one region')
        
        # Creating Header Box Data
        hd_db_0 = pd.read_excel('health-analytics-data.xlsx', sheet_name='disease_burden_1')
        nb_villages = hd_db_0['Number of Villages'][hd_db_0['Regions']==region_2].max()
        nb_schools = hd_db_0['Number of Schools'][hd_db_0['Regions']==region_2].max()
        total_population = int(hd_db_0['Total Population'][hd_db_0['Regions']==region_2].max())
        total_population = f"{total_population:,}"
        
        # Creating Header Boxes
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))
        
        # Filling Header Boxes In
        m1.write('')
        m2.metric(label ='Number of Villages', value = nb_villages)
        m3.metric(label ='Number of Schools', value = nb_schools)
        m4.metric(label ='Total Population', value = total_population)
        m5.write('')
        
        # Target Population
        g1, g2 = st.columns((1.5,1.5))
        
        # Health Analytics Data - Target Population Tab Dataframe
        hd_tp = pd.read_excel('health-analytics-data.xlsx', sheet_name='target_pop')
        hd_tp = hd_tp[hd_tp['Region']==region_2]
        
        # Lymphedema vs. Oncho
        plot = go.Figure(data=[go.Bar(
            name = 'LF Lymphedema Management',
            y = hd_tp['LF Lymphedema Management'],
            x = hd_tp['District'],
            marker=dict(color = 'darkseagreen'),
        ),
                              go.Bar(
            name = 'Oncho Round 1',
            y = hd_tp['Oncho Round 1'],
            x = hd_tp['District'],
            marker=dict(color = 'darkgrey'),
        )
        ])

        plot.update_layout(title_text="Lymphedema vs. Oncho",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Target Population Count',
                           template='seaborn')
        
        g1.plotly_chart(plot, use_container_width=True)

        # Adult vs. Child
        plot = go.Figure(data=[go.Bar(
            name = 'SCH School Age Children',
            y = hd_tp['SCH School Age Children'],
            x = hd_tp['District'],
        ), 
                              go.Bar(
            name = 'SCH High Risk Adult',
            y = hd_tp['SCH High Risk Adult'],
            x = hd_tp['District'],
        )
        ])

        plot.update_layout(title_text="Adult vs. Child",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Target Population Count',
                           template='seaborn')

        g2.plotly_chart(plot, use_container_width=True)

        # Choropleth
        g3, g4 = st.columns((3,1))
        
        # Choropleth
        test_df = pd.read_excel('health-analytics-data.xlsx', sheet_name='geo_data')
        test_df = test_df[test_df['Regions']==region_2]
        m = leafmap.Map(tiles="stamentoner", center=(10.984335, -10.964355), zoom=6)
        m.add_heatmap(
            test_df,
            latitude="Latitude",
            longitude="Longitude",
            value="Total Population",
            name="Total Population Map",
            radius=25,
        )
        m.to_streamlit(height=400)

    with st.expander("Five Year Projection of Medicine Need"):

        # Five-year projection of medicine
        g5, g6, g7  = st.columns((1.33, 1.33, 1.33))

        # Health Analytics Data - Disease Burden Tab Dataframe
        hd_db_1 = pd.read_excel('health-analytics-data.xlsx', sheet_name='disease_burden_1')
        hd_db_1 = hd_db_1[hd_db_1['Regions'] == region_2]

        # LF Disease Burden
        hd_lf_db = hd_db_1[hd_db_1['Disease Type']=='LF Disease Burden Code']

        # Oncho Disease Burden
        hd_on_db = hd_db_1[hd_db_1['Disease Type']=='Oncho Disease Burden Code']

        # SCH Disease Burden
        hd_sch_db = hd_db_1[hd_db_1['Disease Type']=='SCH Disease Burden Code']
        
        # STH Disease Burden
        hd_sth_db = hd_db_1[hd_db_1['Disease Type']=='STH Disease Burden Code']

        # Trachoma Disease Burden
        hd_tra_db = hd_db_1[hd_db_1['Disease Type']=='Trachoma Disease Burden Code']

        # Five-year projection of medicine
        # LF Disease Burden
        fig = px.line(hd_lf_db, y="Disease Burden", x="Year", color='Districts')
        
        fig.update_layout(title_text="Albendazole, Diethylcarbamazine, Ivermectin",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Medicine Need',
                           template='seaborn')

        g5.plotly_chart(fig, use_container_width=True)

        # Oncho Disease Burden
        fig = px.line(hd_on_db, y="Disease Burden", x="Year", color='Districts')
        
        fig.update_layout(title_text="Ivermectin, Doxycycline",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Medicine Need',
                           template='seaborn')

        g6.plotly_chart(fig, use_container_width=True)

        # SCH Disease Burden
        fig = px.line(hd_sch_db, y="Disease Burden", x="Year", color='Districts')
        
        fig.update_layout(title_text="Praziquantel, PZQ",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Medicine Need',
                           template='seaborn')

        g7.plotly_chart(fig, use_container_width=True)

        # Five-year projection of medicine - continued
        g8, g9  = st.columns((1.5, 1.5))

        # STH Disease Burden
        fig = px.line(hd_sth_db, y="Disease Burden", x="Year", color='Districts')
        
        fig.update_layout(title_text="Albendazole, Mebendazole",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Medicine Need',
                           template='seaborn')

        g8.plotly_chart(fig, use_container_width=True)

        # Trachoma Disease Burden
        fig = px.line(hd_tra_db, y="Disease Burden", x="Year", color='Districts')
        
        fig.update_layout(title_text="Azithromycin, Tetracycline",
                           title_x=0,
                           margin= dict(l=0,r=10,b=10,t=30), 
                           xaxis_title='', 
                           yaxis_title='Medicine Need',
                           template='seaborn')

        g9.plotly_chart(fig, use_container_width=True)