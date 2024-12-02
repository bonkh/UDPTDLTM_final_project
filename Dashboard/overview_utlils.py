# market_overview.py
import os
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


def display_index_overview(index_data, index_name, header_text, exchange_name):
    latest_data = index_data.iloc[0]
    closing_price = f"{latest_data['closing_price']:.2f}"
    price_change = f"{latest_data['price_change']:.2f}"
    price_change_percentage = f"({latest_data['price_change_percentage']:.2f}%)"

    # Set text color based on price change
    color = "green" if latest_data["price_change"] > 0 else "red"

    # Tooltip content
    tooltip_text = (
        f"This is the {index_name}, represents for all stock in the {exchange_name} exchange . The current price is {closing_price}, "
        f"with a change of {price_change} points, which is a "
        f"{latest_data['price_change_percentage']:.2f}% change."
    )

    st.markdown(
        f"""
        <div class="tooltip tooltip-right" style="display: flex; align-items: center; justify-content: space-between; white-space: nowrap;">
            <!-- Header text căn trái -->
            <div style="font-size: 15px; font-weight: bold; text-align: left; margin-right: 10px;">
                {header_text}:
            </div>
            <!-- Giá trị căn phải -->
            <div style="color: {color}; font-size: 15px; text-align: right;">
                {closing_price} 
                {'▲' if latest_data['price_change'] > 0 else '▼'}{price_change} 
                {price_change_percentage}
            </div>
            <!-- Tooltip -->
            <div class="tooltiptext">
                {tooltip_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def display_stock_overview(selected_row, hovered_label, latest_date):
    color = "green" if selected_row["price_change"] > 0 else "red"
    closing_price = f"{selected_row['closing_price']:.2f}"
    price_change = f"{selected_row['price_change']:.2f}"
    price_change_percentage = f"({selected_row['price_change_percentage']:.2f}%)"

    # Tooltip content
    tooltip_text = (
        f"Giá cổ phiếu đóng cửa của {hovered_label} ngày {latest_date} là {closing_price}, "
        f"thay đổi so với ngày hôm trước là {price_change}, tức {price_change_percentage}."
    )

    # CSS nhúng để hiển thị tooltip
    st.markdown(
        """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 300px;
            background-color: #555;
            color: #fff;
            text-align: center;
            padding: 5px;
            border-radius: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Đặt tooltip phía trên */
            left: 50%;
            margin-left: -150px; /* Căn giữa tooltip */
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Hiển thị thông tin cổ phiếu với tooltip
    st.markdown(
        f"""
        <div class="tooltip" style="display: flex; align-items: center; justify-content: space-between; white-space: nowrap;">
            <!-- Mã cổ phiếu -->
            <div style="font-size: 15px; font-weight: bold; text-align: left; margin-right: 10px;">
                {hovered_label}:
            </div>
            
            <!-- Giá trị và thay đổi -->
            <div style="color: {color}; font-size: 15px; text-align: right;">
                {closing_price} 
                {'▲' if selected_row['price_change'] > 0 else '▼'}{price_change} 
                {price_change_percentage}
            </div>
            
            <!-- Tooltip -->
            <div class="tooltiptext">
                {tooltip_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
criteria_mapping = {
    "listed_shares": "Cổ phiếu niêm yết",
    "shares_outstanding": "Cổ phiếu lưu hành",
    "reference_price": "Giá tham chiếu",
    "ceiling_price": "Giá trần",
    "floor_price": "Giá sàn",
    "total_trading_volume": "Tổng khối lượng giao dịch",
    "total_trading_value": "Tổng giá trị giao dịch",
    "market_capitalization": "Vốn hóa thị trường",
    "opening_price": "Giá mở cửa",
    "closing_price": "Giá đóng cửa",
    "highest_price": "Giá cao nhất",
    "lowest_price": "Giá thấp nhất",
    "difference": "Chênh lệch",
    "average_price": "Giá trung bình",
    "adjusted_closing_price": "Giá đóng cửa điều chỉnh",
    "price_change": "Biến động giá",
    "price_change_percentage": "Tỷ lệ biến động giá",
    "average_buy_price": "Giá mua trung bình",
    "average_sell_price": "Giá bán trung bình",
    "buy_limit": "Giới hạn mua",
    "sell_limit": "Giới hạn bán",
    "matched_orders_volume": "Khối lượng lệnh khớp",
    "matched_orders_value": "Giá trị lệnh khớp",
    "total_orders_placed_buy": "Tổng số lệnh mua đã đặt",
    "total_orders_placed_sell": "Tổng số lệnh bán đã đặt",
    "total_volume_placed_buy": "Tổng khối lượng mua đã đặt",
    "total_volume_placed_sell": "Tổng khối lượng bán đã đặt",
    "agreements_volume": "Khối lượng thỏa thuận",
    "agreements_value": "Giá trị thỏa thuận"
    }
criteria_english = list(criteria_mapping.keys())

column_explanations = {
    "market_capitalization": "Vốn hóa thị trường của công ty, tính bằng giá cổ phiếu nhân với số lượng cổ phiếu đang lưu hành.",
    "reference_price": "Giá tham chiếu, thường là giá mở cửa của phiên giao dịch trước đó, dùng để so sánh với giá hiện tại.",
    "ceiling_price": "Giá trần của cổ phiếu, giới hạn giá tối đa mà cổ phiếu có thể đạt được trong ngày giao dịch.",
    "floor_price": "Giá sàn của cổ phiếu, giới hạn giá tối thiểu mà cổ phiếu có thể đạt được trong ngày giao dịch.",
    "opening_price": "Giá mở cửa của cổ phiếu trong phiên giao dịch, là giá của cổ phiếu tại thời điểm bắt đầu giao dịch.",
    "closing_price": "Giá đóng cửa của cổ phiếu, là giá cổ phiếu cuối cùng được giao dịch khi kết thúc phiên giao dịch.",
    "highest_price": "Giá cao nhất của cổ phiếu trong phiên giao dịch, là mức giá cao nhất mà cổ phiếu đạt được trong suốt ngày giao dịch.",
    "lowest_price": "Giá thấp nhất của cổ phiếu trong phiên giao dịch, là mức giá thấp nhất mà cổ phiếu đạt được trong suốt ngày giao dịch.",
    "total_trading_volume": "Khối lượng giao dịch tổng cộng của cổ phiếu trong phiên giao dịch, thể hiện số lượng cổ phiếu đã được mua/bán.",
    "total_trading_value": "Giá trị giao dịch tổng cộng của cổ phiếu trong phiên giao dịch, tính bằng giá trị của số cổ phiếu đã giao dịch (khối lượng giao dịch * giá)."
}


def load_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load external HTML file (optional)
def load_html(file_name):
    with open(file_name, "r") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

tooltip_dict = {
    "market_overview_page": "Trang này cung cấp thông tin tổng quan về thị trường, bao gồm các chỉ số chính, xu hướng và biến động.",
    "up_to_date" : "Chọn ngày cuối cùng mà thông tin về thị trường được tổng hợp, việc xem xét tổng quan thị trường trên nhiều ngày khác nhau sẽ đem đến sự so sánh về những biến đổi trên thị trường qua nhiều ngày.",
    "stock_exchange_explaination" : """
                                        Sàn chứng khoán là nơi mà các chứng khoán như cổ phiếu, trái phiếu được giao dịch. Hiện nay, ở Việt Nam đang có ba sàn chứng khoán chính sau:
                                        <ul>
                                            <li>HOSE: Sở Giao dịch Chứng khoán TP.HCM</li>
                                            <li>HNX: Sở Giao dịch Chứng khoán Hà Nội </li>
                                            <li>UPCoM: Thị trường giao dịch cổ phiếu của các công ty chưa niêm yết trên sàn chứng khoán chính thức.</li>
                                        </ul>
                                        Mỗi sàn có những đặc điểm và danh sách cổ phiếu riêng biệt. Chọn tất cả hoặc từng sàn để xem các cổ phiếu giao dịch tại đó.
                                    """,

    "industry_explaination" : """ Lựa chọn ngành kinh tế mà bạn muốn xem, có thể là bất kỳ ngành nào từ danh sách các ngành hiện có.
                                    Các mã chứng khoán sẽ được nhóm theo ngành tương ứng của chúng để dễ dàng so sánh và phân tích."""
                                    ,
    
}