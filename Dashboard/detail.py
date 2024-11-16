import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import pandas as pd
import numpy as np


# Moving average functions
def SMA(df, period, column):
    return df[column].rolling(window=period).mean()

def EMA(df, period, column):
    return df[column].ewm(span=period, adjust=False).mean()

def WMA(df, period, column):
    weights = np.arange(1, period + 1)
    return df[column].rolling(period).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

def VWMA(df, period, column, volume_column='total_trading_volume'):
    return (df[column] * df[volume_column]).rolling(period).sum() / df[volume_column].rolling(period).sum()

# Generalized MA function
def calculate_ma(df, period=30, column="Price", ma_type="SMA"):
    if ma_type == "SMA":
        return SMA(df, period, column)
    elif ma_type == "EMA":
        return EMA(df, period, column)
    elif ma_type == "WMA":
        return WMA(df, period, column)
    elif ma_type == "VWMA":
        return VWMA(df, period, column)
    else:
        raise ValueError("Invalid MA type. Choose 'SMA', 'EMA', 'WMA', or 'VWMA'.")

# Function to add EMA indicators to data
def add_ema(data, periods):
    for period in periods:
        data[f'EMA_{period}'] = EMA(data, period, 'closing_price')
    return data

# RSI calculation function
def add_rsi(data, window=14):
    delta = data['closing_price'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# MACD calculation function
def add_macd(data):
    data['MACD'] = EMA(data, 12, 'closing_price') - EMA(data, 26, 'closing_price')
    data['Signal_Line'] = EMA(data, 9, 'MACD')
    return data

# Buy/Sell Signals Function
def buy_n_sell(df, stock_code, col='closing_price', period1=20, period2=50, period3=200, MA_type='SMA'):
    df = df[df['stock_code'] == stock_code].sort_values('trade_date').copy()
    df['line1'] = calculate_ma(df, period=period1, column=col, ma_type=MA_type)
    df['line2'] = calculate_ma(df, period=period2, column=col, ma_type=MA_type)
    df['line3'] = calculate_ma(df, period=period3, column=col, ma_type=MA_type)

    df['Signal'] = np.where(df["line1"] > df["line2"], 1, 0)
    df['Position'] = df['Signal'].diff()
    df['Buy'] = np.where(df['Position'] == 1, df[col], np.nan)
    df['Sell'] = np.where(df['Position'] == -1, df[col], np.nan)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['trade_date'],
        open=df['opening_price'],
        high=df['highest_price'],
        low=df['lowest_price'],
        close=df[col],
        name='Price'
    ))

    # MA lines
    fig.add_trace(go.Scatter(x=df['trade_date'], y=df['line1'], name=f'Short-Term MA ({period1})', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['trade_date'], y=df['line2'], name=f'Medium-Term MA ({period2})', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df['trade_date'], y=df['line3'], name=f'Long-Term MA ({period3})', line=dict(color='green')))

    # Buy/Sell signals
    fig.add_trace(go.Scatter(x=df['trade_date'][df['Position'] == 1], y=df[col][df['Position'] == 1], mode='markers',
                             marker=dict(symbol='triangle-up', color='green', size=10), name='Buy Signal'))
    fig.add_trace(go.Scatter(x=df['trade_date'][df['Position'] == -1], y=df[col][df['Position'] == -1], mode='markers',
                             marker=dict(symbol='triangle-down', color='red', size=10), name='Sell Signal'))

    fig.update_layout(title=f'Trading Signals for {stock_code}', xaxis_title='Date', yaxis_title='Price', height=600)
    st.plotly_chart(fig)