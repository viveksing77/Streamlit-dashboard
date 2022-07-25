import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("/home/vivek/Desktop/Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("MOTOR COLLISION IN NEW YORK CITY")
st.markdown("This application is a streamlit dashboard that can be used to analyse motor vehicle collisions in NYC")

@st.cache(persist=True)

def load_data(nrows):
    #parsing the data and time according to pandas
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    #Streamlit crashes when we put blank data so we have to drop NaN values
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    #we are using lambda function to apply the lowercase 
    lowercase = lambda x:str(x).lower()
    #now we are changing the names of the columns
    data.rename(lowercase, axis='columns', inplace=True)
    # renaming some columns to something simpler using dictionary format
    data.rename(columns = {'crash date_crash time':'date/time'}, inplace=True)
    data.rename(columns= {'number of persons injured':'injured_persons'}, inplace=True)
    data.rename(columns = {'number of pedestrians injured':'injured_pedestrians'}, inplace=True)
    data.rename(columns = {'number of cyclist injured':'injured_cyclists'}, inplace=True)
    data.rename(columns = {'number of motorist injured':'injured_motorists'}, inplace=True)

    return data 

data = load_data(100000)
original_data = data
#print('number of persons injured' in data.columns)
st.header("Where are the most people injured in NYC?")
#Streamlit allows you to add interactivity directly into the app with the help of widgets
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
#plotting data on map now and to use st.map there has to be column name latitude and longitude
st.map(data.query('injured_persons>= @injured_people')[["latitude", "longitude"]].dropna(how='any'))

st.header("How many collisions occur during a given time of day?")
#now we will add hour of the day interative dropdown
hour = st.slider("Hour to look at ", 0, 23)
#now we are equating hours to 'date/time' subset
data = data[data['date/time'].dt.hour==hour]
()
st.markdown("Vehicle collisions between %i:00 and %i:00"%(hour ,(hour+1) % 24))

#midpoint of latitude and logitude and it has to be from new york city or it doesnt make any sense
midpoint = ( np.average(data['latitude']), np.average(data['longitude']) )
#making a 3D plot with pydeck
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude":midpoint[0],
        "longitude":midpoint[1],
        "zoom":11,
        "pitch":50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1 ) %24))
#now we will filter the data
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
# now we will plot the filtered data into histogram
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
#now creating a dataframe so plotly can plot our data
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y ='crashes', hover_data = ['minute', 'crashes'], height=400)
st.write(fig)

#which is the deadliest road for NYC
st.header("Top 5 dangerous street by affected type")
select = st.selectbox("Affected type of people ", ['Pedestrians', 'Cyclists', 'Motorists'])
#but for above we need unfiltered data not for time/date and latitude,longitude
if select == 'Pedestrians':
    st.write(original_data.query('injured_pedestrians > = 1')[['on street name', 'injured_pedestrians']].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any'))

elif select == 'Cyclists':
    st.write(original_data.query('injured_cyclists > = 1')[['on street name', 'injured_cyclists']].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any'))

else:
    st.write(original_data.query('injured_motorists > = 1')[['on street name', 'injured_motorists']].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any'))

#making a checkbox so it wont show raw data as default
if st.checkbox('Show raw data', False):

    st.subheader('Raw Data')
    st.write(data)
