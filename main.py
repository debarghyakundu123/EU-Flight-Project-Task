import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Streamlit App Title
st.title("✈️ European Flight Tracker Dashboard")
st.write("Upload your SQLite database file (`airports.db`) to monitor flight details in real time.")

# File Upload
uploaded_file = st.file_uploader("Upload SQLite Database", type=["db"])

if uploaded_file:
    # Save uploaded file
    with open("airports.db", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Connect to database
    conn = sqlite3.connect("airports.db")
    cursor = conn.cursor()

    # Load flight data
    query = "SELECT * FROM flight_data"
    flights_df = pd.read_sql(query, conn)

    # Close DB connection
    conn.close()

    # Convert delay to numeric (if exists)
    if "delay" in flights_df.columns:
        flights_df["delay"] = pd.to_numeric(flights_df["delay"], errors="coerce")

    # Search Bar
    search_query = st.text_input("🔍 Search Flight Number:", "")
    if search_query:
        flights_df = flights_df[flights_df["flight_number"].str.contains(search_query, na=False)]

    # Filter by Status
    status_filter = st.selectbox("📌 Filter by Flight Status:", ["All"] + list(flights_df["status"].unique()))
    if status_filter != "All":
        flights_df = flights_df[flights_df["status"] == status_filter]

    # Highlight Delays
    flights_df["Delay Status"] = flights_df["delay"].apply(lambda x: "🚨 Delayed (2+ hrs)" if x and x > 120 else "✅ On Time")

    # Show Data
    st.subheader("📋 Flight Data Table")
    st.dataframe(flights_df)

    # Visualization: Delays
    st.subheader("📊 Flight Delay Distribution")
    fig = px.histogram(flights_df, x="delay", title="Flight Delays", nbins=20, color_discrete_sequence=["red"])
    st.plotly_chart(fig)

    # Visualization: Flight Statuses
    st.subheader("📊 Flight Status Breakdown")
    fig2 = px.pie(flights_df, names="status", title="Flight Status Breakdown", hole=0.3)
    st.plotly_chart(fig2)

else:
    st.warning("⚠️ Please upload `airports.db` to continue.")

