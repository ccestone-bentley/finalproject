'''
Program Name: finalproject.py
Name: Christopher Cestone
Date: 5/7/23
Description: This program was designed off of the airport-codes_csv.csv file
            I created a home page, a map, and 3 charts all relating to that dataset.
            This was a challenging, but fun project to work on! I learned a lot about
            python packages that made completing the graphs and charts much easier.
'''


import streamlit as st
import pandas as pd
from PIL import Image
import folium.plugins
import streamlit_folium as stfol
from haversine import haversine
import plotly.express as px

df_air1 = pd.read_csv("airport-codes_csv.csv")
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.width', None, 'max_colwidth', None)

# Welcome page for website-- inlcludes overview
def welcomepage():
    st.title("Ready to explore the world? Let's check out all of airports to find where we can go!", anchor=None)
    st.header("Check out our other pages to learn more")
    airport_image_path = Image.open("airports.jpg")
    st.image(airport_image_path,caption=None, use_column_width=True)

# Creating my first dataframe, however I need to seperate out the coordinates field to make it graphable
# dataframe with new column to seperate the coordinates field

#The continent field is also not reading correctly, as NA means North America, not None
df_air1['continent'].fillna("NA",inplace=True)
# creating latitude and longitude fields, and splitting the old coordinates field at the comma (as that is what seperated the two)
df_air1[['lon', 'lat']] = df_air1['coordinates'].str.split(",", expand=True).astype(float)
df_air1.drop('coordinates', axis=1, inplace=True)

# pulling out other fields that will never be used: ident, gps_code, iata_code, local_code
df_air1 = df_air1.drop(columns =['ident','iata_code','local_code','gps_code','iso_region','municipality'])

# filtering out "closed"-- there is no sense in displaying airports that are no longer operational
df_air1 = df_air1.drop(df_air1[df_air1['type'] == 'closed'].index)


# In this section, I am creating the main body of this website's features.
# Users will be able to choose what airport type they want, then enter in the latitude and longitude of the destination
# They then will use a slider to choose their maximum distnace from the location in miles
# This is certainly the most impressive feature and work that I completed in my assignment

def flightcalculator():
    st.title(":blue[Flight Calculator: Choose how to fly, where you're flying to, and how close you will be to the airport]")
    st.header("The Boston area is set as default, but feel free to enter whatever coordinates you want!")

    # Airport Selector Feature: This will let you choose what type of airport you want to fly out of
    airport_selector = st.radio("Choose your airport type", df_air1.type.unique(),)
    # Entering Lat and Lon (will accept negative and positive numbers) -- as it is based on N,S,E,W
    chosen_lat = st.number_input('Enter the latitude of your destination',value=42)
    chosen_lon = st.number_input("Enter the longitude of your destinaton ",value=-71)

    # Slider feature to determine how far are you willing to be from an airport
    max_distance = st.slider("Enter the maximum distance from location in miles",0,400,50)

    # creating a new dataframe-- df_air_sorted-- this will be used in creating a column chart to show where the nearest airports are
    df_air_sorted = df_air1[df_air1['type'] == airport_selector]

    # I then used the haversine package to calculate the distance between the longitude and latitude points of the destination to the airport.
    df_air_sorted['distance'] = df_air_sorted.apply(lambda row: haversine((chosen_lat, chosen_lon), (row['lat'], row['lon']), unit='mi'), axis=1)

    # From here, I then made sure that my dataframe will only produce results that are under the result that is set by the slider
    df_air_sorted = df_air_sorted[df_air_sorted['distance'] < max_distance]

    # I then sorted the dataframe so that the results that are given are in order of closest to farthest
    df_air_sorted = df_air_sorted.sort_values(by=['distance'])
    # showing dataframe above graph
    st.write(df_air_sorted)

    # print based on the lats and lons of the df_filtered, centered at chosen lat and lons, and zoom based on your distance chosen
    def printmap():
        st.write(
            "<FONT COLOR=RED><u><h1 style='text-align: center;'>Here are airports near your chosen coordinates:</h1></u></FONT>",
            unsafe_allow_html=True)
        map = folium.Map(location=[chosen_lat, chosen_lon], zoom_start=7)
        for index, row in df_air_sorted.iterrows():
            marker = folium.Marker(location=[row['lat'], row['lon']], tooltip=row['name'])
            marker.add_to(map)
        folium.plugins.Fullscreen(position='topleft').add_to(map)
        stfol.folium_static(map)
        st.header("Get Ready for Takeoff!")
    printmap()

# I am making this pie chart to compare the types of airports, but not including closed airports (as done in df1)
# This pie chart is also dynamic, and uses plotly to make it dynamic, allowing you to select what airport types you want to compare
def airportsbytype():
    st.title("These visuals will show the different types of airports, and the percentage breakdowns")
    # Dropping columns not needed in the analysis
    df_air2 = df_air1.drop(columns =['name','elevation_ft','lon','lat','iso_country','continent'])
    type_counts = df_air2['type'].value_counts()
    # Using Plotly's syntax to create the charts
    fig = px.pie(type_counts,values=type_counts.values,names=type_counts.index,title="Airport Type Breakdown",labels=type_counts.index,width=600,height=400,color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(legend=dict(font=dict(size=25)))
    st.plotly_chart(fig)

def airportsbycontinent():
    st.title("Comparison of Airports by Continent")
    # sorting out the columns to let me only work with the continent field
    df_air3 = df_air1.drop(columns=['name', 'elevation_ft', 'lon', 'lat', 'type', 'iso_country'])
    # renaming the continents so the Abbreviations are changed into the actual names
    df_air3['Continent'] = df_air3['continent'].replace({'AF': 'Africa', 'AN': 'Antarctica', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America', 'OC': 'Oceania', 'SA': 'South America'})
    # Creating a count to determine how many airports are in each continent
    df_air3_continent = df_air3.groupby('Continent')['Continent'].agg(Count='count').reset_index()
    # I then decided to sort these so they are ordered from smallest to largest
    df_air3_continent.sort_values(by='Count', inplace=True)
    # using plotly package to structure the bar chart
    fig = px.bar(df_air3_continent, x='Continent', y='Count', color='Continent')
    fig.update_layout(title="Airports by Continent", xaxis_title="Continent", yaxis_title="Number of Airports")
    fig.update_layout(legend=dict(font=dict(size=20)))
    st.plotly_chart(fig)
    st.write("North America has an insane amount of airports compared to the rest of the world, having more than the following 4 continents combined!")
# As my last graph in this program, I want to create a bar graph that shows the 10 airports that have the highest elevation by feet
# The X axis will be the airport names--> only the top 10 in elevation
# the Y axis will be the elevation number, which is in feet
# I then will sort based on continent, to then let us see what continent has airports with the highest elevation
def toptenhighestairports():
    st.title("Top 10 Highest Airports in the World")
    # sorting out the columns I need to do this analysis-- I will only need the airport names and their elevation
    df_air4 = df_air1.drop(columns=['lon', 'lat', 'type', 'iso_country'])
    # Sorting the values from highest to lowest
    df4_sorted = df_air4.sort_values(by='elevation_ft', ascending=False)
    # pulling out the top 10 values
    df4_top_10= df4_sorted.head(10)
    # using the plotly syntax to creat the bar chart
    fig = px.bar(df4_top_10, x='name', y='elevation_ft', color='continent', title='Top 10 Highest Airports',hover_data=['elevation_ft', 'continent', 'name'])
    fig.update_layout(title="Airports by Elevation", xaxis_title="Airport Name", yaxis_title="Elevation (feet)")
    fig.update_layout(legend=dict(font=dict(size=10)))
    st.plotly_chart(fig)
    # Written Analysis
    st.write("North America has the highest airport elevation of them all, yet only has one in the top 10. Asia follows with the second highest airport, and is responsible for 5 of the top 10. South America follows, with 4 in the top 10. ")


# I created this sidebar to house my functions-- this is pretty a main() function of my program, which lets users switch between the pages that I made

def sidebar():
    with st.sidebar:
        st.title("Airports Around the World")
        page_select = st.selectbox("Check Out Our Pages:", ('Home Page', 'Flight Calculator', "Airports by Type", "Airports by Continent","Top 10 Highest Airports by Elevation"))
    if page_select == "Home Page":
        welcomepage()
    if page_select == "Flight Calculator":
        flightcalculator()
    if page_select == "Airports by Type":
        airportsbytype()
    if page_select == "Airports by Continent":
        airportsbycontinent()
    if page_select == "Top 10 Highest Airports by Elevation":
        toptenhighestairports()

sidebar()
