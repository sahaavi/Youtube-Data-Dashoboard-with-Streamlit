# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 12:40:40 2022

@author: avish
"""

#import libs
import pandas as pd #for data manipulation
import numpy as np #for working with arrays and different data structures
import plotly.graph_objects as go #isolate and adjust plotly graphs
import plotly.express as px #make assumptions of the data
import streamlit as st #for hosting our dashboard
from datetime import datetime

#define functions
def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try: 
        return props if v < 0 else None
    except:
        pass
    
def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try: 
        return props if v > 0 else None
    except:
        pass    
    
def audience_simple(country):
    """Show top represented countries"""
    if country == 'US':
        return 'USA'
    elif country == 'IN':
        return 'India'
    else:
        return 'Other'

@st.cache #so it doesn't laod every single time when we reload the page
def load_data():
    #load data
    df_agg = pd.read_csv('Data/Aggregated_Metrics_By_Video.csv').iloc[1:,:] #storing without the first row
    df_agg_sub = pd.read_csv('Data/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('Data/All_Comments_Final.csv')
    df_perf = pd.read_csv('Data/Video_Performance_Over_Time.csv')
    
    #feature engineering
    df_agg.columns = ['Video', 'Video_title', 'Video_pub­lish_time', 'Com­ments_ad­ded',
           'Shares', 'Dis­likes', 'Likes', 'Sub­scribers_lost',
           'Sub­scribers_gained', 'RPM(USD)', 'CPM(USD)',
           'Av­er­age_per­cent­age_viewed(%)', 'Av­er­age_view_dur­a­tion',
           'Views', 'Watch_time(hours)', 'Sub­scribers',
           'Your_es­tim­ated_rev­en­ue(USD)', 'Im­pres­sions',
           'Im­pres­sions_click-through_rate(%)'] #renaming the columns
    df_agg['Video_pub­lish_time'] = pd.to_datetime(df_agg['Video_pub­lish_time']) #converting to datetime object
    df_agg['Av­er­age_view_dur­a­tion'] = df_agg['Av­er­age_view_dur­a­tion'].apply(lambda x: datetime.strptime(x,'%H:%M:%S')) #converting object to datetime representation
    df_agg['Avg_duration_sec'] = df_agg['Av­er­age_view_dur­a­tion'].apply(lambda x: x.second + x.minute*60 + x.hour*3600) #converting time to seconds
    df_agg.sort_values('Video_pub­lish_time', ascending = False, inplace = True) #sorting in descending order according to video publish time
    df_perf['Date'] = pd.to_datetime(df_perf['Date'])
    
    return df_agg, df_agg_sub, df_comments, df_perf

#create dataframes from the function 
df_agg, df_agg_sub, df_comments, df_perf = load_data()

#additional data engineering for aggregated data 
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video_pub­lish_time'].max() - pd.DateOffset(months =12) #finding out the 1 year previous date from the most recent published video
median_agg = df_agg_diff[df_agg_diff['Video_pub­lish_time'] >= metric_date_12mo].median() #median of all columns using only last 1 year data

#create differences from the median for values 
#Just numeric columns 
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)

#merge daily data with publish data to get delta 
df_time_diff = pd.merge(df_perf, df_agg.loc[:,['Video','Video_pub­lish_time']], left_on ='External Video ID', right_on = 'Video')
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video_pub­lish_time']).dt.days

# get last 12 months of data rather than all data 
date_12mo = df_agg['Video_pub­lish_time'].max() - pd.DateOffset(months =12)
df_time_diff_yr = df_time_diff[df_time_diff['Video_pub­lish_time'] >= date_12mo]

# get daily view data (first 30), median & percentiles 
views_days = pd.pivot_table(df_time_diff_yr,index= 'days_published',values ='Views', aggfunc = [np.mean,np.median,lambda x: np.percentile(x, 80),lambda x: np.percentile(x, 20)]).reset_index()
views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:,['days_published','median_views','80pct_views','20pct_views']] 
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()


#################Building Dashboard/App#################
   
#sidebar
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics','Individual Video Analysis'))

#Total picture
#Aggregated metrics
if add_sidebar == 'Aggregate Metrics':
    st.write("Ken Jee YouTube Aggregated Data")
    df_agg_metrics = df_agg[['Video_pub­lish_time','Views','Likes','Sub­scribers','Shares','Com­ments_ad­ded','RPM(USD)','Av­er­age_per­cent­age_viewed(%)',
                         'Avg_duration_sec']]
    metric_date_6mo = df_agg_metrics['Video_pub­lish_time'].max() - pd.DateOffset(months =6)
    metric_date_12mo = df_agg_metrics['Video_pub­lish_time'].max() - pd.DateOffset(months =12)
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video_pub­lish_time'] >= metric_date_6mo].median()
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video_pub­lish_time'] >= metric_date_12mo].median()

    #Creating columns in Streamlit
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    count = 0
    for i in metric_medians6mo.index:
        with columns[count]:
            delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i] #percent chage over time
            st.metric(label= i, value = round(metric_medians6mo[i],1), delta = "{:.2%}".format(delta))
            count += 1
            if count >= 5:
                count = 0

    #get date information / trim to relevant data 
    df_agg_diff['Publish_date'] = df_agg_diff['Video_pub­lish_time'].apply(lambda x: x.date())
    df_agg_diff_final = df_agg_diff.loc[:,['Video_title','Publish_date','Views','Likes','Sub­scribers','Shares','Com­ments_ad­ded','RPM(USD)','Av­er­age_per­cent­age_viewed(%)',
                             'Avg_duration_sec']]
    
    df_agg_numeric_lst = df_agg_diff_final.median().index.tolist() #numeric columns
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format #formatting percentage
    
    st.dataframe(df_agg_diff_final.style.hide().applymap(style_negative, props='color:red;').applymap(style_positive, props='color:green;').format(df_to_pct)) #showing the dataframe along with colors

#Individual video analysis    
if add_sidebar == 'Individual Video Analysis':
    videos = tuple(df_agg['Video_title']) 
    st.write("Individual Video Performance")
    video_select = st.selectbox('Pick a Video:', videos)
    
    agg_filtered = df_agg[df_agg['Video_title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(audience_simple)
    agg_sub_filtered.sort_values('Is Subscribed', inplace= True)
    
    fig = px.bar(agg_sub_filtered, x ='Views', y='Is Subscribed', color ='Country', orientation ='h')
    #order axis 
    st.plotly_chart(fig)
    
    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0,30)]
    first_30 = first_30.sort_values('days_published')
    
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],
                    mode='lines',
                    name='20th percentile', line=dict(color='purple', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],
                        mode='lines',
                        name='50th percentile', line=dict(color='black', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],
                        mode='lines', 
                        name='80th percentile', line=dict(color='royalblue', dash ='dash')))
    fig2.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['Views'].cumsum(),
                        mode='lines', 
                        name='Current Video' ,line=dict(color='firebrick',width=8)))
        
    fig2.update_layout(title='View comparison first 30 days',
                   xaxis_title='Days Since Published',
                   yaxis_title='Cumulative views')
    
    st.plotly_chart(fig2)