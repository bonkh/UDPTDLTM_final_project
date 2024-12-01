# data_loader.py
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine
import streamlit as st

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

    return data_frames


@st.cache_data
def load_data(table_name):
    engine = create_engine(
        "postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c"
    )
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)


@st.cache_data
def load_stock_data():
    engine = create_engine(
        "postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c"
    )
    return pd.read_sql("SELECT * FROM stock_data", engine)
