import streamlit as st
import pandas as pd
import mysql.connector
import requests
import time

# Set page config
st.set_page_config(page_title="Live Flight Dashboard", layout="wide")

# API Key (Replace with actual API key)
API_KEY = "d33617411919dcdb29b7c3c20a2e8537"
API_URL = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&limit=10"

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="FlightData"
    )

# Function to fetch real-time flight data from API
def fetch_real_time_flights():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        flight_data = []
        for flight in data['data']:
            flight_data.append({
                "Flight Number": flight['flight']['iata'],
                "Airline": flight['airline']['name'],
                "Departure": flight['departure']['iata'],
                "Arrival": flight['arrival']['iata'],
                "Scheduled Departure": flight['departure']['scheduled'],
                "Estimated Departure": flight['departure']['estimated'],
                "Scheduled Arrival": flight['arrival']['scheduled'],
                "Estimated Arrival": flight['arrival']['estimated'],
                "Status": flight['flight_status']
            })
        return pd.DataFrame(flight_data)
    else:
        st.error("Failed to fetch flight data.")
        return pd.DataFrame()

# Function to fetch flights from MySQL
def fetch_flight_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT flight_number, airline, scheduled_departure, estimated_departure,
           scheduled_arrival, estimated_arrival, status
    FROM Flights
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    columns = ["Flight Number", "Airline", "Scheduled Departure", "Estimated Departure", 
               "Scheduled Arrival", "Estimated Arrival", "Status"]
    
    return pd.DataFrame(data, columns=columns)

# Sidebar options
st.sidebar.title("✈️ Flight Tracker")
option = st.sidebar.selectbox("Choose Data Source:", ["Live API Data", "Database Data"])

# Fetch data based on selection
if option == "Live API Data":
    st.sidebar.info("Fetching real-time flight data from API...")
    flights_df = fetch_real_time_flights()
else:
    st.sidebar.info("Fetching stored flight data from database...")
    flights_df = fetch_flight_data()

# Display Data
st.title("📊 Real-Time Flight Dashboard")
st.dataframe(flights_df)

# Search Functionality
search_query = st.text_input("Search by Flight Number or Airport Code:")
if search_query:
    filtered_df = flights_df[
        flights_df["Flight Number"].str.contains(search_query, na=False) |
        flights_df["Departure"].str.contains(search_query, na=False) |
        flights_df["Arrival"].str.contains(search_query, na=False)
    ]
    st.dataframe(filtered_df)

# Refresh Button
if st.button("🔄 Refresh Data"):
    time.sleep(1)
    st.experimental_rerun()
