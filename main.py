import streamlit as st
import sqlite3
import pandas as pd

# Connect to the database
DB_FILE = "airports.db"

def get_tables():
    """Fetch all table names from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return [row[0] for row in conn.execute(query).fetchall()]

def get_table_data(table_name):
    """Fetch data from a specific table."""
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)

def run_query(query):
    """Execute a custom SQL query."""
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql(query, conn)

# Streamlit UI
st.title("Airport Database Viewer ✈️")

# Sidebar for table selection
tables = get_tables()
selected_table = st.sidebar.selectbox("Select a Table", tables)

# Display table data
if selected_table:
    st.subheader(f"Data from {selected_table}")
    df = get_table_data(selected_table)
    st.dataframe(df)

# Custom SQL Query Input
st.subheader("Run Custom SQL Query")
query = st.text_area("Enter your SQL query:", value="SELECT * FROM airports LIMIT 10;")

if st.button("Execute Query"):
    try:
        query_result = run_query(query)
        st.dataframe(query_result)
    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("Upload new database file:")
uploaded_file = st.sidebar.file_uploader("Upload .db file", type=["db"])

if uploaded_file:
    with open(DB_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("Database updated! Refresh the app.")
