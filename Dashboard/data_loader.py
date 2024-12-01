# data_loader.py
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

conn_str = os.getenv('DATABASE_RENDER')
engine = create_engine(conn_str)


@st.cache_data
def load_all_tables():
    tables = ["stock_data", "stock_info", "financial_metrics", "stock_index"]
    data_frames = {}

    with ThreadPoolExecutor() as executor:
        future_to_table = {executor.submit(load_data, table): table for table in tables}
        for future in as_completed(future_to_table):
            table = future_to_table[future]
            try:
                data_frames[table] = future.result()
            except Exception as e:
                st.error(f"Error loading {table}: {e}")
                data_frames[table] = pd.DataFrame()

    print("Data loaded successfully !!!")
    return data_frames


@st.cache_data
def load_data(table_name):
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)


@st.cache_data
def load_stock_data():
    return pd.read_sql("SELECT * FROM stock_data", engine)
