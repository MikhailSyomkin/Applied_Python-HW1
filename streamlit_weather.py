import streamlit as st
import requests
import asyncio
import aiohttp
import nest_asyncio 
import pandas as pd
import numpy as np

def get_weather(city, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'cod': response.status_code, 'message': response.json().get('message', 'Error')}

st.title('Temperature Data Analysis')
uploaded_file = st.file_uploader('Load historical data', type='csv')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    city_list = df['city'].unique()
    selected_city = st.selectbox('Choose a city', df['city'].unique())
    city_data = df[df['city'] == selected_city]
    st.write(f'Данные для {selected_city}:', city_data)
    
    st.write('Description:')
    st.write(df['temperature'].describe())
    
    st.subheader('Time Series')
    plt.figure(figsize=(10, 5))
    plt.plot(city_data['timestamp'], city_data['temperature'], label='Temperature', color='blue')
    
    anomalies = df[df.anomaly_flg == 1]
    plt.scatter(anomalies['timestamp'], anomalies['temperature'], color='red', label='Anomalies')
    plt.xlabel('Date')
    plt.ylabel('Temperature')
    plt.legend()
    st.pyplot(plt)
    
    st.subheader('Seasonal profiles')
    city_data['Month'] = pd.to_datetime(city_data['timestamp']).dt.month
    seasonal_profile = city_data.groupby('Month')['Temperature'].agg(['mean', 'std'])
    st.write('Average Seasonal Temperature:', seasonal_profile)
    seasonal_profile.plot(kind='bar', y='mean', yerr='std', color='skyblue', legend=False)
    plt.xlabel('Month')
    plt.ylabel('Temperature')
    st.pyplot(plt)

api_key = st.text_input('API key requred')
current_season = st.text_input('Season')

if api_key:
    st.subheader('Current Temperature')
    if selected_city:
        weather = get_weather(selected_city, api_key)
        if weather.get('cod') == 200:
            current_temp = weather['main']['temp']
            st.write(f'''Current temperature in {city}: {current_temp}''')
            if current_temp >= df[(df.city == selected_city)&(df.season == current_season)].anomaly_criteria_high.unique()[0]:
                normality = 'anomaly, too high'
            if current_temp <= df[(df.city == selected_city)&(df.season == current_season)].anomaly_criteria_low.unique()[0]:
                normality = 'anomaly, too low'
            else:
                normality = 'normal temperature'
            print (f'''Temperature status: {normality}''')
        else:
            st.error({'cod':401, 'message': 'Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.'})
