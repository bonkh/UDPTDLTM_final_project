import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from overview import get_filtered_data
from detail import *


CONN_STRING =  'postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c'

@st.cache_data
def load_data(table_name):
    engine = create_engine(CONN_STRING)
    try:
        return pd.read_sql(f"SELECT * FROM {table_name}", engine)
    except Exception as e:
        st.error(f"Error loading {table_name}: {e}")
        return pd.DataFrame()
    


@st.cache_data
def load_all_tables():
    tables = ["stock_data", "stock_info", "financial_metrics", "stock_index"]
    data_frames = {}

    with ThreadPoolExecutor() as executor:
        # Submit each table loading task to the executor
        future_to_table = {executor.submit(load_data, table): table for table in tables}
        for future in as_completed(future_to_table):
            table = future_to_table[future]
            try:
                data_frames[table] = future.result()
            except Exception as e:
                st.error(f"Error loading {table}: {e}")
                data_frames[table] = pd.DataFrame()  # Assign empty DataFrame on error

    return data_frames

# Load all data
data_frames = load_all_tables()
stock_data = data_frames.get("stock_data")
stock_info = data_frames.get("stock_info")
stock_index = data_frames.get("stock_index")
stock_financial_metrics = data_frames.get("financial_metrics")

with st.sidebar:
    selected_tab = st.selectbox("Select Tab for Sidebar Options", ["Market Overview", "Detail Information"])


if selected_tab == "Market Overview":
    st.header("Market Overview")



    

    stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'], errors='coerce')
    stock_data = stock_data.sort_values(by='trade_date').reset_index(drop=True)

    col1, col2, col3 = st.columns(3)  # Adjust the number of columns as needed

    # In the first column, display a multiselect for Exchange
    with col1:
        exchange_filter = st.multiselect(
            "Select Stock Exchanges",
            options=["HOSE", "HNX", "UPCOM", "All"],  # Options for stock exchanges
            default=["All"]  # Default to "All"
        )

        if "All" in exchange_filter:
            # If "All" is selected, include all exchanges
            filtered_stock_info = stock_info
        else:
            # Filter based on selected exchanges
            filtered_stock_info = stock_info[stock_info['exchange'].isin(exchange_filter)]

    with col2:
        industry_filter = st.multiselect(
            "Select Industries",
            options=['All'] + list(stock_info['industry_name'].unique()),
            default=["All"] 
        )

        if "All" not in industry_filter:
            filtered_stock_info = filtered_stock_info[filtered_stock_info['industry_name'].isin(industry_filter)]



    latest_date = stock_data['trade_date'].max()
    latest_data = stock_data[stock_data['trade_date'] == latest_date][['stock_code', 'total_trading_value']]

    merged_data = pd.merge(filtered_stock_info, latest_data, left_on='code', right_on='stock_code', how='inner')

    latest_price_change = stock_data.sort_values('trade_date').drop_duplicates('stock_code', keep='last')
    latest_price_change = latest_price_change[['stock_code', 'price_change_percentage']]
    merged_data = pd.merge(merged_data, latest_price_change, left_on='code', right_on='stock_code', how='left')
    merged_data = merged_data.dropna(subset=['price_change_percentage'])


    industry_totals = merged_data.groupby('industry_name')['total_trading_value'].sum().reset_index()
    industry_totals = industry_totals.rename(columns={'total_trading_value': 'industry_total_trading_value'})

    
    top_bottom_df = pd.merge(merged_data, industry_totals, on='industry_name')


    top_bottom_df['color'] = top_bottom_df['price_change_percentage'].apply(
        lambda x: '0' if x == 0 else ('1' if x > 0 else '-1')
    )
    
    market_overview_fig = px.treemap(
        data_frame=top_bottom_df,
        path=['industry_name', 'code'], 
        values='total_trading_value', 
        hover_data=['total_trading_value', 'price_change_percentage'], 
        hover_name='code',
        color='color',
        color_discrete_map={'-1': 'red', '0': 'yellow', '1': 'green'}
    )

    market_overview_fig.update_layout(
        margin=dict(t=50, l=20, r=20, b=20),
        font=dict(size=10, weight="bold"),
    )

    market_overview_fig.data[0].texttemplate = "%{label}<br>%{customdata[1]:.2f}%"
    market_overview_fig.data[0].textfont = dict(size=12, weight="bold") 
    market_overview_fig.data[0].textposition = "middle center" 


    market_overview_fig.update_traces(root_color="lightgrey",
                                        marker=dict(cornerradius=5),
        
                                    ) 

    colors_list = list(market_overview_fig.data[0]['marker']['colors'])
    colors_list = ['white' if color  == '#000004' else color for color in colors_list]
    market_overview_fig.data[0]['marker']['colors'] = tuple(colors_list)

    st.plotly_chart(market_overview_fig, use_container_width=True)


    st.subheader("Exchange Market")

    col_1, col_2  = st.columns(2) 
    with col_1:
        periods = st.slider('Chọn khoảng thời gian (ngày)', 30, 400, 180)
        end_date = pd.Timestamp.today()
        start_date = end_date - pd.Timedelta(days=periods)

     
        end_date = pd.Timestamp.today()
        start_date = end_date - pd.Timedelta(days=periods)

        stock_index['trading_date'] = pd.to_datetime(stock_index['trading_date'], errors='coerce')
        stock_index = stock_index.sort_values(by='trading_date').reset_index(drop=True)

        index_code = st.multiselect("Index Code", options=["All"] + stock_index['stock_code'].unique().tolist())

        if "All" in index_code:
            selected_index_code = stock_index['stock_code'].unique().tolist()
        else:
            selected_index_code = index_code
        index_data = stock_index[(stock_index['stock_code'].isin(selected_index_code)) & (stock_index['trading_date'] >= pd.Timestamp(start_date))]



        index_fig = px.line(
        index_data,
        x='trading_date', 
        y='opening_price', 
        color='stock_code',
        title="Open Price Over Time by Stock Code",
        labels={'opening_price': 'Open Price', 'trade_date': 'Trade Date'}
        )

        st.plotly_chart(index_fig, use_container_width=True)




    st.subheader("Top impact in VN-index")

    latest_market_data =  stock_data[stock_data['trade_date'] == latest_date][['stock_code', 'market_capitalization', 'price_change_percentage']]
    total_market_cap = latest_market_data['market_capitalization'].sum()

    latest_market_data['weight'] = latest_market_data['market_capitalization'] / total_market_cap

    latest_market_data['impact_on_index'] = latest_market_data['weight'] * latest_market_data['price_change_percentage']

    vn_index_data = latest_market_data.sort_values(by='impact_on_index', ascending=False)

    top_positive = vn_index_data.sort_values(by='impact_on_index', ascending=False).head(10)
    top_negative = vn_index_data.sort_values(by='impact_on_index').head(10)
    filtered_data = pd.concat([top_positive, top_negative])

    # Add color column based on impact direction
    filtered_data['color'] = filtered_data['impact_on_index'].apply(lambda x: 'green' if x > 0 else 'red')

        # Plotly bar chart
    impact_on_vn_index_fig = px.bar(
        filtered_data,
        x='stock_code',
        y='impact_on_index',
        color='color',
        title="Impact of Stocks on VN-Index",
        labels={'impact_on_index': 'Impact on VN-Index', 'stock_code': 'Stock Code'},
        color_discrete_map={'green': 'green', 'red': 'red'}
    )

    # Customize layout
    impact_on_vn_index_fig.update_layout(
        xaxis_title="Stock Code",
        yaxis_title="Impact on VN-Index",
        showlegend=False,
        margin=dict(t=50, l=25, r=25, b=25)
    )

    st.plotly_chart(impact_on_vn_index_fig, use_container_width=True)


    st.subheader("Top 10 by metrics")

    stock_financial_metrics['date'] = pd.to_datetime(stock_financial_metrics['date'], errors='coerce')
    stock_financial_metrics = stock_financial_metrics.sort_values(by='date').reset_index(drop=True)
    st.table(stock_financial_metrics.head(10))

    latest_date = stock_financial_metrics['date'].max()
    latest_finance_data = stock_financial_metrics[stock_financial_metrics['date'] == latest_date]

    metrics = {
    "P/E": "pe",
    "P/B": "pb",
    "EPS": "eps",
    }

    # Create tabs dynamically
    tabs = st.tabs(list(metrics.keys()))

    # Populate each tab with data
    for tab, (tab_name, column) in zip(tabs, metrics.items()):
        with tab:
            sorted_data = latest_finance_data.sort_values(by=column, ascending=False).head(10)
            st.table(sorted_data)


elif selected_tab == "Detail Information":
    # # Get filtered data for Market Overview
    filtered_data = get_filtered_data(stock_info, stock_data)

    # Create and display plots in the main area
    fig1 = px.line(
        filtered_data,
        x='trade_date', 
        y='opening_price', 
        color='stock_code',
        title="Open Price Over Time by Stock Code",
        labels={'opening_price': 'Open Price', 'trade_date': 'Trade Date'}
    )

    fig2 = px.line(
        filtered_data,
        x='trade_date', 
        y='closing_price', 
        color='stock_code',
        title="Close Price Over Time by Stock Code",
        labels={'closing_price': 'Close Price', 'trade_date': 'Trade Date'}
    )

    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

    for code in filtered_data['stock_code'].unique():
        sub_data = filtered_data[filtered_data['stock_code'] == code]
        buy_n_sell(sub_data, code)

