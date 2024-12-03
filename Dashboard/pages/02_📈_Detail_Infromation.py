import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
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
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from math import ceil, sqrt
import datetime
import warnings
from models.chroma_loader import load_existing_chroma_db
from models.rag_retriever_handler_dashboard import generate_answer

warnings.filterwarnings("ignore")

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY")
)

def setup_page():
    st.set_page_config(
        page_title="Detail Stock Information ",
        page_icon="📈",
        layout="wide",
    )

setup_page()

def remove_json_formatting(input_text):
    # Loại bỏ dấu ```json và ``` nếu chúng có trong input_text
    cleaned_text = input_text.strip("```json").strip("```").strip()
    return cleaned_text

# @st.cache_data 
# def load_stock_data():
#     engine = create_engine('postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c')

#     return pd.read_sql("SELECT * FROM stock_data", engine)

# def load_stock_info():
#     engine = create_engine('postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c')

#     return pd.read_sql("SELECT * FROM stock_info", engine)

# data = load_stock_data()

# info = load_stock_info()

data_frames = st.session_state["data_frames"]
data = data_frames.get("stock_data", pd.DataFrame())
info = data_frames.get("stock_info", pd.DataFrame())

data = data.sort_values(by=['stock_code', 'trade_date'])

data['change'] = data.groupby('stock_code')['closing_price'].pct_change() * 100


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

def lstm_prediction_plotly(df, train_ratio=0.75, epochs=1):
    window_size = 40
    if df.shape[0] < window_size:
        st.write("Not enough data to train the model. Need at least window_size data points.")
        return

    # Đảm bảo cột 'trade_date' là datetime và đặt làm index
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)

    # Chuẩn bị dữ liệu
    df_new = df[['closing_price']]
    dataset = df_new.values
    train_size = ceil(df.shape[0] * train_ratio)
    train = df_new[:train_size]
    valid = df_new[train_size:]
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)
    
    # Chuẩn bị dữ liệu train
    x_train, y_train = [], []
    for i in range(window_size, len(train)):
        x_train.append(scaled_data[i-window_size:i, 0])
        y_train.append(scaled_data[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    # Xây dựng mô hình LSTM
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)),
        LSTM(units=50),
        Dense(1)
    ])
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Huấn luyện mô hình
    model.fit(x_train, y_train, epochs=epochs, batch_size=1, verbose=2)
    
    # Chuẩn bị dữ liệu validate
    inputs = df_new[len(df_new) - len(valid) - window_size:].values
    inputs = scaler.transform(inputs.reshape(-1, 1))
    
    x_validate = []
    for i in range(window_size, inputs.shape[0]):
        x_validate.append(inputs[i-window_size:i, 0])
    x_validate = np.array(x_validate)
    x_validate = np.reshape(x_validate, (x_validate.shape[0], x_validate.shape[1], 1))
    
    # Dự đoán giá
    predicted_price = model.predict(x_validate)
    predicted_price = scaler.inverse_transform(predicted_price)
    valid['Predictions'] = predicted_price

    # Biểu đồ dự đoán LSTM
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train.index, y=train['closing_price'], mode='lines', name='Train'))
    fig.add_trace(go.Scatter(x=valid.index, y=valid['closing_price'], mode='lines', name='Valid'))
    fig.add_trace(go.Scatter(x=valid.index, y=valid['Predictions'], mode='lines', name='Prediction'))
    fig.update_layout(title="Dự đoán giá cổ phiếu bằng LSTM", xaxis_title="Thời gian", yaxis_title="Giá",
                      xaxis=dict(type='date', tickformat='%b %Y'), height=600, autosize=True)
    
    st.plotly_chart(fig)

def lstm_future_prediction(df, train_ratio=0.75, epochs=1, future_months=1):
    # Kiểm tra cột 'trade_date' có tồn tại không
    if 'trade_date' not in df.columns:
        st.write("Column 'trade_date' not found in the DataFrame.")
        return

    window_size = 40
    if df.shape[0] < window_size:
        st.write("Not enough data to train the model. Need at least window_size data points.")
        return

    # Đảm bảo cột 'trade_date' là datetime và đặt làm index
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)

    # Chuẩn bị dữ liệu
    df_new = df[['closing_price']]
    dataset = df_new.values
    train_size = ceil(df.shape[0] * train_ratio)
    train = df_new[:train_size]
    valid = df_new[train_size:]
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)
    
    # Chuẩn bị dữ liệu train
    x_train, y_train = [], []
    for i in range(window_size, len(train)):
        x_train.append(scaled_data[i-window_size:i, 0])
        y_train.append(scaled_data[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    # Xây dựng mô hình LSTM
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)),
        LSTM(units=50),
        Dense(1)
    ])
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Huấn luyện mô hình
    model.fit(x_train, y_train, epochs=epochs, batch_size=1, verbose=2)
    
    # Chuẩn bị dữ liệu validate
    inputs = df_new[len(df_new) - len(valid) - window_size:].values
    inputs = scaler.transform(inputs.reshape(-1, 1))
    
    x_validate = []
    for i in range(window_size, inputs.shape[0]):
        x_validate.append(inputs[i-window_size:i, 0])
    x_validate = np.array(x_validate)
    x_validate = np.reshape(x_validate, (x_validate.shape[0], x_validate.shape[1], 1))
    
    # Dự đoán giá
    predicted_price = model.predict(x_validate)
    predicted_price = scaler.inverse_transform(predicted_price)
    valid['Predictions'] = predicted_price

    # Các dự đoán trong tương lai (tính theo tháng)
    future_days = future_months * 30
    last_window_data = scaled_data[-window_size:]

    future_predictions = []

    for _ in range(future_days):
        next_prediction = model.predict(last_window_data.reshape(1, window_size, 1))
        future_predictions.append(next_prediction[0, 0])
        last_window_data = np.append(last_window_data[1:], next_prediction)

    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    
    # Ngày tương lai để biểu diễn
    last_date = df_new.index[-1]
    future_dates = [last_date + datetime.timedelta(days=i) for i in range(1, future_days + 1)]

    # Biểu đồ dự đoán LSTM
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train.index, y=train['closing_price'], mode='lines', name='Train'))
    fig.add_trace(go.Scatter(x=valid.index, y=valid['closing_price'], mode='lines', name='Valid'))
    fig.add_trace(go.Scatter(x=valid.index, y=valid['Predictions'], mode='lines', name='Prediction'))
    fig.add_trace(go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions'))
    fig.update_layout(title="Dự đoán giá cổ phiếu bằng LSTM", xaxis_title="Thời gian", yaxis_title="Giá",
                      xaxis=dict(type='date', tickformat='%b %Y'), height=600, autosize=True)
    
    st.plotly_chart(fig)



# Streamlit UI
st.title('Dashboard phân tích cổ phiếu')


# Sidebar
# st.sidebar.header('Cài Đặt')

st.sidebar.subheader('Chọn Mã Cổ Phiếu')
stock_code = st.sidebar.selectbox('Mã cổ phiếu', options=data['stock_code'].unique(), index=data['stock_code'].unique().tolist().index('VCB'))

# Lọc dữ liệu theo mã cổ phiếu đã chọn
stock_data = data[data['stock_code'] == stock_code]

# in tail của stock_data
# st.write(stock_data.tail())

# Lấy ngày gần nhất và giá trị tương ứng
latest_row = stock_data.iloc[-1]
current_date = latest_row['trade_date']
current_price = latest_row['closing_price']
change_percentage = latest_row['change']

# Merge dữ liệu từ data và info
merged_data = pd.merge(data, info, left_on='stock_code', right_on='code', how='left')

# Lọc dữ liệu theo mã cổ phiếu được chọn
stock_data = merged_data[merged_data['stock_code'] == stock_code]

# Lấy thông tin công ty
company_name = stock_data['name'].iloc[0]  # Tên công ty
industry_name = stock_data['industry_name'].iloc[0]  # Ngành nghề

# Tạo các cột để hiển thị từng thông tin bên cạnh nhau
col1, col2, col3, col4 = st.columns(4)

# Màu sắc cho Change (%)
background_color = "rgba(144,238,144,0.8)" if change_percentage > 0 else "rgba(255,182,193,0.8)"  # Xanh hoặc đỏ nhạt
text_color = "green" if change_percentage > 0 else "red"
arrow = "▲" if change_percentage > 0 else "▼"

# Tên cổ phiếu
with col1:
    st.markdown(
        f"""
        <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; text-align: center;">
            <b style="color: #444;">Mã cổ phiếu</b><br>
            <span style="color: #0066cc; font-size: 20px;">{stock_code}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Ngày hiện tại
with col2:
    st.markdown(
        f"""
        <div style="background-color: #f8f8ff; padding: 10px; border-radius: 5px; text-align: center;">
            <b style="color: #444;">Ngày hiện tại</b><br>
            <span style="color: #444; font-size: 20px;">{current_date}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Giá hiện tại
with col3:
    st.markdown(
        f"""
        <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; text-align: center;">
            <b style="color: #444;">Giá hiện tại</b><br>
            <span style="color: {text_color}; font-size: 20px;">{current_price:,.2f} VND</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Change (%)
with col4:
    st.markdown(
        f"""
        <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; text-align: center;">
            <b style="color: #444;">Change (%)</b><br>
            <span style="color: {text_color}; font-size: 20px;">{arrow} {change_percentage:.2f}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Hiển thị thông tin công ty
st.markdown(
    f"""
    <div style="
        background-color: #f9f9f9; 
        border-radius: 8px; 
        padding: 16px; 
        margin-bottom: 16px; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    ">
        <h4 style="color: #4CAF50; margin-bottom: 8px;">Thông tin tổ chức</h4>
        <p><strong>Tên đầy đủ:</strong> {company_name}</p>
        <p><strong>Ngành nghề:</strong> {industry_name}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Ngày mới nhất trong dữ liệu
today = stock_data['trade_date'].max()

# Chuyển đổi cột 'trade_date' thành pd.Timestamp nếu cần
stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'])

# Giao diện chọn khoảng thời gian
# st.subheader("Chọn khoảng thời gian cho biểu đồ nến")
time_range = st.radio(
    "Khoảng thời gian",
    options=['1W', '2W', '1M', '3M', '6M', '1Y', 'YTD', 'Toàn bộ dữ liệu'],
    index=7,  # Đặt mặc định là "Toàn bộ dữ liệu"
    horizontal=True  # Hiển thị các nút theo chiều ngang
)

# Lựa chọn ngày bắt đầu
if time_range == '1W':
    start_date = today - pd.Timedelta(weeks=1)
elif time_range == '2W':
    start_date = today - pd.Timedelta(weeks=2)
elif time_range == '1M':
    start_date = today - pd.DateOffset(months=1)
elif time_range == '3M':
    start_date = today - pd.DateOffset(months=3)
elif time_range == '6M':
    start_date = today - pd.DateOffset(months=6)
elif time_range == '1Y':
    start_date = today - pd.DateOffset(years=1)
elif time_range == 'YTD':
    start_date = pd.Timestamp(year=today.year, month=1, day=1)
else:
    start_date = stock_data['trade_date'].min()

# Đảm bảo `start_date` là kiểu pd.Timestamp
start_date = pd.Timestamp(start_date)


# Lọc dữ liệu theo khoảng thời gian
filtered_data = stock_data[stock_data['trade_date'] >= start_date]

st.sidebar.subheader('Moving Averages')

# tao period
period1 = st.sidebar.selectbox('Short-term MA', [15, 20, 30], index=0)
period2 = st.sidebar.selectbox('Medium-term MA', [50, 80, 100], index=0)
period3 = st.sidebar.selectbox('Long-term MA', [120, 150, 200], index=0)


MA_type = st.sidebar.selectbox('MA Type', ['SMA', 'EMA', 'WMA', 'VWMA'])

buy_n_sell(filtered_data, stock_code=stock_code, col='closing_price', period1=period1, period2=period2, period3=period3, MA_type=MA_type)

# Hiển thị dự đoán LSTM
stock_data = data[data['stock_code'] == stock_code].sort_values(by='trade_date').reset_index(drop=True)
lstm_prediction_plotly(stock_data, train_ratio=0.75, epochs=10)

# Dự đoán giá trong tương lai
stock_data = data[data['stock_code'] == stock_code]
future_months = st.sidebar.selectbox('Future Prediction (months)', [1, 2, 3])
lstm_future_prediction(stock_data, train_ratio=0.75, epochs=10, future_months=future_months)

def remove_json_formatting(input_text):
    # Loại bỏ dấu ```json và ``` nếu chúng có trong input_text
    cleaned_text = input_text.strip("```json").strip("```").strip()
    return cleaned_text


# Chuẩn bị dữ liệu để call OPENAI API để phân tích tình hình cổ phiếu (dựa theo stock_code)
# Chuẩn bị dữ liệu từ DataFrame
data = {
    "stock_code": stock_data["stock_code"].values.tolist(),
    "opening_price": stock_data["opening_price"].values.tolist(),
    "closing_price": stock_data["closing_price"].values.tolist(),
    "highest_price": stock_data["highest_price"].values.tolist(),
    "lowest_price": stock_data["lowest_price"].values.tolist(),
    "reference_price": stock_data["reference_price"].values.tolist(),
    "price_change": stock_data["price_change"].values.tolist(),
    "price_change_percentage": stock_data[
        "price_change_percentage"
    ].values.tolist(),
    "difference": stock_data["difference"].values.tolist(),
    "average_price": stock_data["average_price"].values.tolist(),
    "adjusted_closing_price": stock_data[
        "adjusted_closing_price"
    ].values.tolist(),
    "total_trading_volume": stock_data["total_trading_volume"].values.tolist(),
    "total_trading_value": stock_data["total_trading_value"].values.tolist(),
    "buy_limit": stock_data["buy_limit"].values.tolist(),
    "sell_limit": stock_data["sell_limit"].values.tolist(),
}

# Định nghĩa chuỗi system với các dấu {} được thoát
system = """You are an expert at Stock analysis.  
Here is the context you should refer to:  
Your task is to analyze the stock performance over the past month based on the provided metrics. Use the following data points extracted from the stock dataset:
- stock_code: {stock_code} (Mã cổ phiếu).  
- opening_price: {opening_price} (Giá mở cửa mỗi ngày).  
- closing_price: {closing_price} (Giá đóng cửa mỗi ngày).  
- highest_price: {highest_price} (Giá cao nhất trong ngày).  
- lowest_price: {lowest_price} (Giá thấp nhất trong ngày).  
- reference_price: {reference_price} (Giá tham chiếu để đánh giá mức tăng hoặc giảm).  
- price_change: {price_change} (Sự thay đổi giá trong ngày).  
- price_change_percentage: {price_change_percentage} (Phần trăm thay đổi giá mỗi ngày).  
- difference: {difference} (Mức dao động giá trong ngày).  
- average_price: {average_price} (Giá trung bình giao dịch mỗi ngày).  
- adjusted_closing_price: {adjusted_closing_price} (Giá đóng cửa điều chỉnh, nếu có).  
- total_trading_volume: {total_trading_volume} (Tổng khối lượng giao dịch trong ngày).  
- total_trading_value: {total_trading_value} (Tổng giá trị giao dịch trong ngày).  
- buy_limit: {buy_limit} (Giới hạn mua, thể hiện áp lực mua).  
- sell_limit: {sell_limit} (Giới hạn bán, thể hiện áp lực bán).

Your response must be in Vietnamese and in JSON format with the following structure:  
```json
{{
  "question": "What is the stock performance over the past month?",
  "answer": "Your detailed analysis based on the context and data"
}}
"""


# Định dạng chuỗi với dữ liệu thực tế
formatted_system = system.format(**data)


def handle_analyst(formatted_system):
    messages = [
        {
            "role": "system",
            "content": formatted_system,
        },  # Nội dung từ formatted_system
        {
            "role": "user",
            "content": "What is the stock performance over the past month?",
        },  # Câu hỏi từ người dùng
    ]
    response = llm(messages)
    # load_json
    response_json = remove_json_formatting(response.content)
    response_json = json.loads(response_json)
    return response_json["answer"]


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# Tạo nút "Phân tích cổ phiếu"

with st.spinner("Đang phân tích..."):
    response = handle_analyst(formatted_system)
    st.session_state.analysis_result = response  # Lưu kết quả vào session_state

# Hiển thị kết quả nếu có
if st.session_state.analysis_result:
    with st.container():
        st.write("### Kết quả phân tích:")
        st.write(response)

def load_vectordb(db_path):
    vector_db = load_existing_chroma_db(db_path)
    print(f"Number of documents in vector DB: {len(vector_db.get())}")
    return vector_db


# Thêm thông tin báo về cổ phiếu
if "stock_news" not in st.session_state:
    st.session_state.stock_news = None

with st.spinner("Đang tìm kiếm thông tin cổ phiếu..."):
    vector_db = load_vectordb("vector_db")
    query_news = f"Thông tin cổ phiếu {company_name} {stock_code}"
    output = generate_answer(vector_db, query_news, top_k=10)
    output = json.loads(output)
    links = output["links"]
    titles = output["titles"]
    date = output["date"]
    stock_news = {"links": links, "titles": titles, "date": date}
    st.session_state.stock_news = output


def sorted_news(news):
    news["date"] = [datetime.datetime.strptime(date, "%d/%m/%Y") for date in news["date"]]  # Chuyển đổi ngày thành datetime
    # Sắp xếp theo ngày
    sorted_news = {
        "links": [],
        "titles": [],
        "date": [],
    }
    sorted_news["links"], sorted_news["titles"], sorted_news["date"] = zip(
        *sorted(
            zip(news["links"], news["titles"], news["date"]),
            key=lambda x: x[2],
            reverse=True,
        )
    )
    return sorted_news


# Hiển thị thông tin cổ phiếu
if st.session_state.stock_news:
    with st.container():
        st.write(f"### Tóm tắt các bài báo liên quan cổ phiếu {stock_code}:")
        st.write(output["answer"])
        st.write("### Tin tức mới nhất:")
        sorted_news = sorted_news(st.session_state.stock_news)
        for link, title, date in zip(sorted_news["links"], sorted_news["titles"], sorted_news["date"]):
            st.markdown(f"[{title}]({link}) - {date.strftime('%d/%m/%Y')}")
        

