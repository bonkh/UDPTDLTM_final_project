import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

@st.cache_data 
def load_stock_data():
    engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

    return pd.read_sql("SELECT * FROM stock_data", engine)

def load_stock_info():
    engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

    return pd.read_sql("SELECT * FROM stock_info", engine)

st.title('Stock Data Visualization')


stock_data = load_stock_data()
stock_code_list = stock_data['stock_code'].unique()
sub_data = stock_data[stock_data['stock_code'].isin(stock_code_list[100:110])]

stock_info = load_stock_info()


sub_data = sub_data.sort_values(by=['stock_code', 'trade_date'])

fig = px.line(
    sub_data,
    x='trade_date',
    y='opening_price',
    color='stock_code',
    title="Open Price Over Time by Ticker",
    labels={'opening_price': 'Open Price', 'trade_date': 'Trade Date'},
    line_shape='linear')


fig2 = px.line(
    sub_data,
    x='trade_date', 
    y='closing_price', 
    color='stock_code',
    title="Close Price Over Time by Ticker",
    labels={'close': 'Close Price', 'trade_date': 'Trade Date'}
)

fig3 = px.histogram(
    sub_data,
    x='total_trading_volume',
    color='stock_code',
    title="Trading Volume Distribution by Ticker",
    labels={'volume': 'Trading Volume'},
    nbins=30, 
    marginal='box', 
    opacity=0.7 
)

industry_counts = stock_info['industry_name'].value_counts().reset_index()
industry_counts.columns = ['industry_name', 'count']

fig4 = px.bar(industry_counts, x='industry_name', y='count', 
             title='Count of Companies by Industry',
             labels={'industry_name': 'Industry Name', 'count': 'Count'},
             color='count', 
             text='count')


st.plotly_chart(fig)
st.plotly_chart(fig2)
st.plotly_chart(fig3)
st.plotly_chart(fig4)
