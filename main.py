import streamlit as st
import sqlite3
import pandas as pd
import os

# Absolute path to the database (important for deployment)
DB_FILE = os.path.join(os.path.dirname(__file__), "airports.db")

# Function to get table names (cached for better performance)
@st.cache_data
def get_tables():
    """Fetch all table names from the database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            return [row[0] for row in conn.execute(query).fetchall()]
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return []

# Function to get table data (cached)
@st.cache_data
def get_table_data(table_name):
    """Fetch data from a specific table."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        st.error(f"Failed to load table '{table_name}': {e}")
        return pd.DataFrame()

# Function to run custom SQL queries
def run_query(query):
    """Execute a custom SQL query."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        return pd.DataFrame()

# Streamlit UI
st.title("✈️ Airport Database Viewer")

# Sidebar: Select a table
tables = get_tables()
if tables:
    selected_table = st.sidebar.selectbox("Select a Table", tables)

    # Display selected table data
    st.subheader(f"📊 Data from: {selected_table}")
    df = get_table_data(selected_table)
    st.dataframe(df)
else:
    st.warning("⚠️ No tables found in the database!")

# Custom SQL Query Input
st.subheader("🔍 Run Custom SQL Query")
query = st.text_area("Enter SQL query:", value="SELECT * FROM airports LIMIT 10;")

if st.button("Execute Query"):
    query_result = run_query(query)
    if not query_result.empty:
        st.dataframe(query_result)
