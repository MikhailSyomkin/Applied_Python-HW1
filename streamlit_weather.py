import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_weather(city, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'cod': response.status_code, 'message': response.json().get('message', 'Error')}

st.title('Temperature Data Analysis')
st.text('This is an app designed to allow you to get insights on temperature-related data. To begin, upload a csv file containing histtorical data. We recommend using the preprocessed file from https://github.com/MikhailSyomkin/Applied_Python-HW1/blob/main/df_temp_expanded.csv')
uploaded_file = st.file_uploader('Load historical data (use df_temp_expanded from Git repo)', type='csv')

if uploaded_file:
    file_option = st.selectbox('I used the following file', ['df_temp_expanded.csv', 'Default file (temperature_data.csv)'])
    if file_option == 'Default file (temperature_data.csv)': 
        df = pd.read_csv(uploaded_file)
        df_expanded = pd.DataFrame()
        for city in df.city.unique():
            data = df[(df.city == city)].sort_values('timestamp')
            data['rolling_temperature'] = data['temperature'].rolling(window = 30).mean()
            df_expanded = pd.concat([df_expanded, data])
    
        df_means = df_expanded.groupby(by = ['season', 'city']).rolling_temperature.mean().to_frame().reset_index()
        df_std = df_expanded.groupby(by = ['season', 'city']).rolling_temperature.std().to_frame().reset_index()
    
        df_expanded = df_expanded.merge(df_means, how='left', left_on=['city', 'season'], right_on=['city', 'season']) 
        df_expanded = df_expanded.merge(df_std, how='left', left_on=['city', 'season'], right_on=['city', 'season']) 
        df_expanded = df_expanded.set_axis(['city', 'timestamp',
                                            'temperature', 'season', 'rolling_temperature', 'temperature_mean', 'temperature_std'], axis='columns')
        # df_expanded
        df_expanded['anomaly_criteria_high'] = df_expanded.temperature_mean + 2 * df_expanded.temperature_std
        df_expanded['anomaly_criteria_low'] = df_expanded.temperature_mean - 2 * df_expanded.temperature_std
        # df_expanded
        df_expanded['anomaly_flg'] = ((df_expanded['temperature'] <= df_expanded['anomaly_criteria_low']) | 
                                      (df_expanded['temperature'] >= df_expanded['anomaly_criteria_high'])).astype(int)
        df = df_expanded.copy()
        
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
        seasonal_profile = city_data.groupby('Month')['temperature'].agg(['mean', 'std'])
        st.write('Average Seasonal Temperature:', seasonal_profile)
        seasonal_profile.plot(kind='bar', y='mean', yerr='std', color='skyblue', legend=False)
        plt.xlabel('Month')
        plt.ylabel('Temperature')
        st.pyplot(plt)
        
    else:  
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
        seasonal_profile = city_data.groupby('Month')['temperature'].agg(['mean', 'std'])
        st.write('Average Seasonal Temperature:', seasonal_profile)
        seasonal_profile.plot(kind='bar', y='mean', yerr='std', color='skyblue', legend=False)
        plt.xlabel('Month')
        plt.ylabel('Temperature')
        st.pyplot(plt)

api_key = st.text_input('API key requred to check current temperature')

if api_key:
    st.subheader('Current Temperature')
    if selected_city:
        weather = get_weather(selected_city, api_key)
        if weather.get('cod') == 200:
            current_temp = weather['main']['temp']
            st.write(f'''Current temperature in {selected_city}: {current_temp}''')
            current_season = st.selectbox('Select current season', ['winter', 'spring', 'summer', 'autumn'])
            if current_temp >= df[(df.city == selected_city)&(df.season == current_season)].anomaly_criteria_high.unique()[0]:
                normality = 'anomaly, too high'
            if current_temp <= df[(df.city == selected_city)&(df.season == current_season)].anomaly_criteria_low.unique()[0]:
                normality = 'anomaly, too low'
            else:
                normality = 'normal temperature'
            st.text(f'''Temperature status: {normality}''')
        else:
            st.error({'cod':401, 'message': 'Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.'})
