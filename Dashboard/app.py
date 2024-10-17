import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

@st.cache_data 
def load_data():
    # engine = create_engine('postgresql+psycopg2://postgres:bonkho20092003@localhost:5432/stock_data')
    engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

    return pd.read_sql("SELECT * FROM stock_data", engine)

st.title('Stock Data Visualization')

data = load_data()

fig = px.line(
    data,
    x='trade_date', 
    y='open', 
    color='ticker',
    title="Open Price Over Time by Ticker",
    labels={'open': 'Open Price', 'trade_date': 'Trade Date'}
)

fig2 = px.line(
    data,
    x='trade_date', 
    y='close', 
    color='ticker',
    title="Close Price Over Time by Ticker",
    labels={'close': 'Close Price', 'trade_date': 'Trade Date'}
)

fig3 = px.histogram(
    data,
    x='volume',
    color='ticker',
    title="Trading Volume Distribution by Ticker",
    labels={'volume': 'Trading Volume'},
    nbins=30, 
    marginal='box', 
    opacity=0.7 
)



st.plotly_chart(fig)
st.plotly_chart(fig2)
st.plotly_chart(fig3)


if st.button("Exit App"):
    with open("stop_flag.txt", "w") as f:
        f.write("stop")
    st.write("Exiting the app...")
    st.stop()
