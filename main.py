import streamlit as st
import sqlite3
import pandas as pd
import os

# Get absolute path for the database
DB_FILE = os.path.join(os.path.dirname(__file__), "airports.db")

# Function to check if database exists
def check_database():
    if not os.path.exists(DB_FILE):
        st.error("❌ Database file 'airports.db' not found! Please ensure it is uploaded to the app directory.")
        return False
    return True

# Fetch table names (cached for performance)
@st.cache_data
def get_tables():
    """Retrieve all table names from the database."""
    if not check_database():
        return []
    try:
        with sqlite3.connect(DB_FILE) as conn:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            return [row[0] for row in conn.execute(query).fetchall()]
    except Exception as e:
        st.error(f"⚠️ Error retrieving tables: {e}")
        return []

# Fetch table data (cached)
@st.cache_data
def get_table_data(table_name):
    """Retrieve all rows from a specific table."""
    if not check_database():
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return pd.read_sql(f"SELECT * FROM {table_name} LIMIT 100", conn)  # Limit to 100 rows
    except Exception as e:
        st.error(f"⚠️ Error loading data from {table_name}: {e}")
        return pd.DataFrame()

# Run a custom SQL query
def run_query(query):
    """Execute a custom SQL query."""
    if not check_database():
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"⚠️ SQL Query Error: {e}")
        return pd.DataFrame()

# --- STREAMLIT UI ---
st.title("✈️ Airport Database Viewer")

# Sidebar: Select a table
tables = get_tables()
if tables:
    selected_table = st.sidebar.selectbox("📋 Select a Table", tables)

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
    else:
        st.warning("⚠️ No results found or invalid query.")
