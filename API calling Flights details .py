import requests
import sqlite3
import pandas as pd

# API credentials
API_URL = "https://api.aviationstack.com/v1"
ACCESS_KEY = "d33617411919dcdb29b7c3c20a2e8537"

# List of 6 German airports
german_airports = ["FRA", "MUC", "TXL", "HAM", "DUS", "BER"]  # Frankfurt, Munich, Berlin, etc.

# Initialize SQLite DB
conn = sqlite3.connect("airports.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS flight_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_iata TEXT,
    flight_number TEXT,
    airline TEXT,
    departure_airport TEXT,
    arrival_airport TEXT,
    departure_time_scheduled TEXT,
    departure_time_estimated TEXT,
    arrival_time_scheduled TEXT,
    arrival_time_estimated TEXT,
    status TEXT,
    delay INTEGER,
    FOREIGN KEY(airport_iata) REFERENCES airport_data(iata_code)
)''')

conn.commit()


# Function to fetch flights with specific status
def fetch_flights(status_filter=None):
    for airport in german_airports:
        params = {
            "access_key": ACCESS_KEY,
            "arr_iata": airport,  # Fetching ARRIVED flights
            "flight_status": status_filter if status_filter else None
        }
        
        response = requests.get(f"{API_URL}/flights", params=params)
        data = response.json()
        
        # Debug: Check API response structure
        if "data" not in data:
            print(f"⚠️ No data found for {airport} ({status_filter})")
            continue

        for flight in data["data"]:
            if "departure" in flight and "arrival" in flight:
                flight_status = flight.get("flight_status", "Unknown")

                scheduled_dep = flight["departure"].get("scheduled")
                estimated_dep = flight["departure"].get("estimated")
                scheduled_arr = flight["arrival"].get("scheduled")
                estimated_arr = flight["arrival"].get("estimated")

                departure_airport = flight["departure"].get("airport", "Unknown")
                arrival_airport = flight["arrival"].get("airport", "Unknown")

                # Calculate delay for landed flights
                delay = None
                if flight_status == "landed" and scheduled_arr and estimated_arr:
                    delay = (pd.to_datetime(estimated_arr) - pd.to_datetime(scheduled_arr)).total_seconds() / 60

                cursor.execute('''
                    INSERT INTO flight_data (
                        airport_iata, flight_number, airline,
                        departure_airport, arrival_airport,
                        departure_time_scheduled, departure_time_estimated,
                        arrival_time_scheduled, arrival_time_estimated,
                        status, delay
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    airport,
                    flight["flight"]["iata"] if flight["flight"] else "N/A",
                    flight["airline"]["name"] if flight["airline"] else "Unknown",
                    departure_airport,
                    arrival_airport,
                    scheduled_dep,
                    estimated_dep,
                    scheduled_arr,
                    estimated_arr,
                    flight_status.capitalize(),
                    delay
                ))
                conn.commit()
                print(f"✔️ Stored {flight_status} flight: {flight['flight']['iata']} at {airport} - Delay: {delay}")


# Fetch Landed Flights
fetch_flights("landed")

# Fetch Departures & Arrivals (Scheduled & On Air)
fetch_flights()

# Close DB connection
conn.close()
