import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

import warnings

warnings.filterwarnings("ignore")

@st.cache_data 
def load_stock_data():
    engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

    return pd.read_sql("SELECT * FROM stock_data", engine)

def load_stock_info():
    engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

    return pd.read_sql("SELECT * FROM stock_info", engine)

data = load_stock_data()

# save csv file to read
# data.to_csv('./Data/stock_data.csv', index=False)

# print(data.head())

# st.title('DVN Stock Data')

def SMA(df, period, column):
    return df[column].rolling(window=period).mean()

def EMA(df, period, column):
    return df[column].ewm(span=period, adjust=False).mean()

def WMA(df, period, column):
    weights = list(range(1, period + 1))
    return df[column].rolling(period).apply(lambda prices: np.dot(prices, weights) / sum(weights), raw=True)

def VWMA(df, period, column, volume_column='total_trading_volume'):
    weights = np.arange(1, period + 1)
    return df[column].rolling(window=period).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

# Hàm tổng hợp 4 đường MA
def MA(df, period=30, column="Price", ma_type="SMA"):
    if ma_type == "SMA":
        return SMA(df, period, column)
    elif ma_type == "EMA":
        return EMA(df, period, column)
    elif ma_type == "WMA":
        return WMA(df, period, column)
    elif ma_type == "VWMA":
        return VWMA(df, period, column)
    else:
        raise ValueError("Invalid ma_type. Use 'SMA', 'EMA', 'WMA', or 'VWMA'.")
    


# Update the buy_n_sell function with new column names and stock code filtering
def buy_n_sell(df, stock_code, col='closing_price', period1=20, period2=50, period3=200, MA_type='SMA'):
    df = df[df['stock_code'] == stock_code].copy()  # Filter by stock code
    
    # sort date from oldest to newest
    df = df.sort_values('trade_date').sort_values(by='trade_date', ascending=True)

    # Calculate moving averages
    df['line1'] = MA(df, period=period1, column=col, ma_type=MA_type)
    df['line2'] = MA(df, period=period2, column=col, ma_type=MA_type)
    df['line3'] = MA(df, period=period3, column=col, ma_type=MA_type)

    # Buy/Sell signals
    df['Signal'] = np.where(df["line1"] > df["line2"], 1, 0)
    df['Position'] = df['Signal'].diff()
    df['Buy'] = np.where(df['Position'] == 1, df[col], np.nan)
    df['Sell'] = np.where(df['Position'] == -1, df[col], np.nan)

    # Golden Cross and Death Cross
    df['Golden_Signal'] = np.where(df["line2"] > df["line3"], 1, 0)
    df['Golden_Position'] = df['Golden_Signal'].diff()
    
    df['Golden_Buy'] = np.where(df['Golden_Position'] == 1, df[col], np.nan)
    df['Death_Sell'] = np.where(df['Golden_Position'] == -1, df[col], np.nan)

    # Plotting
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(x=df['trade_date'],
                                  open=df['opening_price'],
                                  high=df['highest_price'],
                                  low=df['lowest_price'],
                                  close=df[col],
                                  name='Giá',
                                  opacity=0.5))

    # MA lines
    fig.add_trace(go.Scatter(x=df['trade_date'],
                             y=df['line1'],
                             mode='lines',
                             name=f'MA ngắn hạn {period1}',
                             line=dict(color='royalblue')))

    fig.add_trace(go.Scatter(x=df['trade_date'],
                             y=df['line2'],
                             mode='lines',
                             name=f'MA trung hạn {period2}',
                             line=dict(color='darkorange')))

    fig.add_trace(go.Scatter(x=df['trade_date'],
                             y=df['line3'],
                             mode='lines',
                             name=f'MA dài hạn {period3}',
                             line=dict(color='seagreen')))

    # Buy/Sell Signals
    fig.add_trace(go.Scatter(x=df['trade_date'][df['Position'] == 1],
                             y=df[col][df['Position'] == 1],
                             mode='markers',
                             marker=dict(symbol='triangle-up', color='green', size=12),
                             name='Buy Signal'))

    fig.add_trace(go.Scatter(x=df['trade_date'][df['Position'] == -1],
                             y=df[col][df['Position'] == -1],
                             mode='markers',
                             marker=dict(symbol='triangle-down', color='red', size=12),
                             name='Sell Signal'))
    
    # Golden/Death Signals
    fig.add_trace(go.Scatter(x=df['trade_date'][df['Golden_Position'] == 1],
                             y=df[col][df['Golden_Position'] == 1],
                             mode='markers',
                             marker=dict(symbol='triangle-up', color='gold', size=16),
                             name='Golden Buy Signal',
                             visible='legendonly'))

    fig.add_trace(go.Scatter(x=df['trade_date'][df['Golden_Position'] == -1],
                             y=df[col][df['Golden_Position'] == -1],
                             mode='markers',
                             marker=dict(symbol='triangle-down', color='maroon', size=16),
                             name='Death Sell Signal',
                             visible='legendonly'))

    # Layout setup
    fig.update_layout(title=f'Biểu đồ nến với tín hiệu mua/bán cho mã {stock_code}',
                      xaxis_title='Thời gian',
                      yaxis_title='Giá',
                      autosize=True,
                      height=600)

    st.plotly_chart(fig)

# Streamlit UI
st.title('Stock Analysis Dashboard')

# Sidebar
st.sidebar.header('Cài Đặt')

st.sidebar.subheader('Chọn Mã Cổ Phiếu')
stock_code = st.sidebar.selectbox('Mã cổ phiếu', options=data['stock_code'].unique(), index=data['stock_code'].unique().tolist().index('VCB'))
st.sidebar.subheader('Moving Averages')

# tao period
period1 = st.sidebar.selectbox('Short-term MA', [15, 20, 30], index=1)
period2 = st.sidebar.selectbox('Medium-term MA', [50, 80, 100], index=0)
period3 = st.sidebar.selectbox('Long-term MA', [120, 150, 200], index=2)


MA_type = st.sidebar.selectbox('MA Type', ['SMA', 'EMA', 'WMA', 'VWMA'])

buy_n_sell(data, stock_code=stock_code, col='closing_price', period1=period1, period2=period2, period3=period3, MA_type=MA_type)