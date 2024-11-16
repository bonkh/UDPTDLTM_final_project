# market_overview.py

import pandas as pd
import streamlit as st

def get_filtered_data(stock_info, stock_data):
    # Market Overview Inputs (sidebar)
    stock_exchange = st.sidebar.multiselect("Stock Exchange", options=["All"] + stock_info['exchange'].unique().tolist())

    if "All" in stock_exchange:
        selected_exchanges = stock_info['exchange'].unique().tolist()
    else:
        selected_exchanges = stock_exchange

    filtered_industries = stock_info[stock_info['exchange'].isin(selected_exchanges)]['industry_name'].unique().tolist()
    stock_industry = st.sidebar.multiselect("Stock Industry", options=["All"] + filtered_industries)

    if "All" in stock_industry:
        selected_industries = filtered_industries
    else:
        selected_industries = stock_industry 

    filtered_codes = stock_info[stock_info['industry_name'].isin(selected_industries)]['code'].unique().tolist()
    stock_code = st.sidebar.multiselect("Stock Code", options=["All"] + filtered_codes)

    if "All" in stock_code:
        selected_codes = filtered_codes
    else:
        selected_codes = stock_code 

    # Time Period Selection
    periods = st.sidebar.slider('Select Time Period (in days)', 30, 400, 180)

    end_date = pd.Timestamp.today()
    start_date = end_date - pd.Timedelta(days=periods)

    # Prepare the stock data based on user selections
    stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'], errors='coerce')
    stock_data = stock_data.sort_values(by='trade_date').reset_index(drop=True)
    data = stock_data[(stock_data['stock_code'].isin(selected_codes)) & (stock_data['trade_date'] >= pd.Timestamp(start_date))]

    return data
