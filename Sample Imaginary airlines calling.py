import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

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
    id INTEGER PRIMARY KEY AUTOINCREMENT,fa
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
    delay INTEGER
)''')

conn.commit()

# Insert 10 imaginary delayed flights
imaginary_flights = []
for i in range(1, 11):
    scheduled_arr = datetime.utcnow() - timedelta(hours=3)  # Flight was scheduled 3 hours ago
    estimated_arr = scheduled_arr + timedelta(minutes=140 + i * 5)  # Delayed by 140+ minutes

    # Ensure delay is always positive
    delay_minutes = max(0, (estimated_arr - scheduled_arr).total_seconds() // 60)

    imaginary_flights.append((
        "TXL",  # Random airport
        f"IM{i}123",  # Imaginary flight number
        f"Fake Airlines {i}",  # Fake airline
        "Imaginary Departure Airport",
        "Imaginary Arrival Airport",
        (scheduled_arr - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),  # Fake departure time
        (estimated_arr - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),  # Estimated departure time
        scheduled_arr.strftime("%Y-%m-%d %H:%M:%S"),  # Scheduled arrival
        estimated_arr.strftime("%Y-%m-%d %H:%M:%S"),  # Estimated arrival
        "Landed",
        delay_minutes  # Corrected delay
    ))

cursor.executemany('''
    INSERT INTO flight_data (
        airport_iata, flight_number, airline,
        departure_airport, arrival_airport,
        departure_time_scheduled, departure_time_estimated,
        arrival_time_scheduled, arrival_time_estimated,
        status, delay
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', imaginary_flights)

conn.commit()
print("✅ 10 imaginary delayed flights inserted successfully with correct delays!")

# Close DB connection
conn.close()
