# market_overview.py
import os
import re
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
    "listed_shares": ["Cổ phiếu niêm yết", "Số lượng cổ phiếu niêm yết cho thấy quy mô tổng thể của các công ty trên sàn chứng khoán. Nếu một công ty có số lượng cổ phiếu niêm yết lớn, điều này có thể cho thấy công ty đó có tầm ảnh hưởng lớn hơn trong cơ cấu thị trường. Các công ty lớn thường có nhiều cổ phiếu niêm yết và có thể chiếm tỷ trọng lớn trong thị trường."],
    "shares_outstanding": ["Cổ phiếu lưu hành", "Số lượng cổ phiếu lưu hành phản ánh mức độ phân tán cổ phiếu trên thị trường và ảnh hưởng đến thanh khoản."],
    "reference_price": ["Giá tham chiếu", "Giá tham chiếu là mức giá được sử dụng để xác định giá mở cửa trong một phiên giao dịch, ảnh hưởng đến sự biến động giá trong suốt ngày giao dịch."],
    "ceiling_price": ["Giá trần", "Giá trần và giá sàn cho biết phạm vi dao động của cổ phiếu trong phiên giao dịch."],
    "floor_price": ["Giá sàn", "Giá trần và giá sàn cho biết phạm vi dao động của cổ phiếu trong phiên giao dịch."],
    "total_trading_volume": ["Tổng khối lượng giao dịch", "Khối lượng giao dịch lớn có thể chỉ ra sự quan tâm mạnh mẽ của nhà đầu tư đối với cổ phiếu, giúp đánh giá tính thanh khoản của cổ phiếu đó. Nếu một cổ phiếu có khối lượng giao dịch lớn, có thể điều này cho thấy rằng cổ phiếu đó đang được mua bán nhiều, ảnh hưởng mạnh mẽ đến giá trị thị trường."],
    "total_trading_value": ["Tổng giá trị giao dịch", "Giá trị giao dịch tổng thể cho thấy mức độ đầu tư vào một cổ phiếu. Một cổ phiếu có giá trị giao dịch cao có thể cho thấy rằng các nhà đầu tư đang tập trung mạnh mẽ vào đó. Điều này giúp xác định những cổ phiếu nào đang thu hút sự chú ý lớn từ các nhà đầu tư và có thể ảnh hưởng lớn đến giá trị thị trường."],
    "market_capitalization": ["Vốn hóa thị trường", "Vốn hóa thị trường cho biết quy mô của công ty trên thị trường, ảnh hưởng mạnh đến cơ cấu thị trường."],
    "opening_price": ["Giá mở cửa", "Sự thay đổi giữa giá mở cửa và giá đóng cửa có thể chỉ ra xu hướng của cổ phiếu trong suốt phiên giao dịch."],
    "closing_price": ["Giá đóng cửa", "Sự thay đổi giữa giá mở cửa và giá đóng cửa có thể chỉ ra xu hướng của cổ phiếu trong suốt phiên giao dịch."],
    "price_change": ["Biến động giá", "Biến động giá cho thấy mức độ thay đổi của cổ phiếu so với thời điểm trước đó. Cổ phiếu có sự thay đổi lớn trong giá sẽ có ảnh hưởng mạnh mẽ đến cơ cấu thị trường. Biến động giá lớn có thể chỉ ra sự thay đổi lớn trong tâm lý của nhà đầu tư."],
    "price_change_percentage": ["Tỷ lệ biến động giá", "Tỷ lệ biến động giá giúp hiểu mức độ thay đổi giá của cổ phiếu trong một khoảng thời gian. Tỷ lệ biến động giá lớn cho thấy cổ phiếu có sự thay đổi mạnh mẽ trong giá trị. Các cổ phiếu này có thể có ảnh hưởng lớn đến tổng thể thị trường."],
    "matched_orders_volume": ["Khối lượng lệnh khớp", "Khối lượng lệnh khớp phản ánh mức độ giao dịch thực tế giữa các bên trên thị trường. Nếu một cổ phiếu có khối lượng lệnh khớp lớn, điều này có thể chỉ ra rằng cổ phiếu đó có sự quan tâm lớn từ cả nhà đầu tư mua và bán. Thông qua khối lượng lệnh khớp, bạn có thể nhận thấy những cổ phiếu có giao dịch tích cực, phản ánh sự sôi động và thanh khoản của cổ phiếu đó."],
    "matched_orders_value": ["Giá trị lệnh khớp", "Giá trị lệnh khớp phản ánh tổng giá trị các giao dịch đã được thực hiện giữa các bên. Khi giá trị lệnh khớp lớn, điều này có thể cho thấy rằng có nhiều giao dịch lớn được thực hiện, thường là các lệnh lớn hoặc các giao dịch của tổ chức, ảnh hưởng mạnh đến tổng giá trị thị trường. Đây là một chỉ báo quan trọng về sự sôi động của thị trường và mức độ quan tâm của các nhà đầu tư lớn."],
    "agreements_volume": ["Khối lượng thỏa thuận", "Khối lượng thỏa thuận thể hiện số lượng cổ phiếu đã được giao dịch qua các thỏa thuận, thường là những giao dịch ngoài sàn hoặc giao dịch giữa các tổ chức lớn. Khối lượng thỏa thuận lớn có thể cho thấy rằng các giao dịch thỏa thuận giữa các tổ chức hoặc nhà đầu tư lớn đang diễn ra, có thể phản ánh sự thay đổi trong cơ cấu sở hữu hoặc sự chuyển nhượng quyền sở hữu cổ phiếu. Các thỏa thuận này có thể không ảnh hưởng ngay lập tức đến giá cổ phiếu nhưng lại có tác động lâu dài đến cấu trúc thị trường."],
    "agreements_value": ["Giá trị thỏa thuận", "Giá trị thỏa thuận cho thấy tổng giá trị của các giao dịch thỏa thuận đã được thực hiện. Một cổ phiếu có giá trị thỏa thuận lớn có thể chỉ ra rằng các giao dịch thỏa thuận lớn đang xảy ra giữa các tổ chức hoặc nhà đầu tư lớn, ảnh hưởng mạnh mẽ đến thị trường trong dài hạn. Đây cũng là chỉ báo cho thấy sự biến động hoặc sự thay đổi trong cơ cấu sở hữu của các cổ phiếu này."]
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

finance_metric_features_mapping = {
    "foreign_buy" : "Nước ngoài mua",
    "percent_foreign_ownership" : "Tỉ lệ sở hữu nước ngoài",
    "cash_dividend": "Giá trị cổ tức",
    "dividend_yield" : "Tỷ suất cổ tức",
    "beta" : "Chỉ số Beta",
    "eps" : "EPS",
    "pe" : "PE",
    "forward_pe" : "Forward PE",
    "bvps": "BVPS",
    "pb" : "P/B"
}

def load_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load external HTML file (optional)
def load_html(file_name):
    with open(file_name, "r") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

def remove_html_tags(text):
    return re.sub(r"<[^>]+>", "", text)



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
    "zone_size_explaination" : """Các cổ phiếu sẽ được hiển thị với kích thước dựa trên tiêu chí này.
                                Các tiêu chí này có thể bao gồm vốn hóa thị trường, giao dịch hàng ngày, hoặc bất kỳ tiêu chí nào phù hợp với nhu cầu phần tích của bạn.
                                Ở đây, tiêu chí mặc định sẽ là tổng khối lượng giao dịch trong ngày.""",

    "stock_index_change" : """Đây là biểu đồ đường thể hiện sự biến động của các chỉ số index, đại diện cho các sàn chứng khoán theo từng khoảng thời gian.
                            Cho phép chúng ta theo dõi, cũng như quan sát được các biến đọng về giá, từ đó có được cái nhìn tổng quan về thị trường hiện tại.
                            """
}

import pandas as pd

def calculate_percentage_changes(df):
    """
    Calculate percentage changes for different time periods (%D, %W, %M, %Q, %YTD, %Y)
    for each stock index in the provided dataframe.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'trading_date', 'stock_code', and 'closing_price'.

    Returns:
    pd.DataFrame: A DataFrame with percentage changes for each stock code.
    """
    # Convert 'trading_date' to datetime
    df['trading_date'] = pd.to_datetime(df['trading_date'])

    # Extract date-related features (year, month, quarter, week) from 'trading_date'
    df['year'] = df['trading_date'].dt.year
    df['month'] = df['trading_date'].dt.month
    df['quarter'] = df['trading_date'].dt.quarter
    df['week'] = df['trading_date'].dt.isocalendar().week

    # List to store results for each stock code
    result = []

    # Loop over each unique stock code
    for stock_code in df['stock_code'].unique():
        # Filter data for each stock code
        stock_data = df[df['stock_code'] == stock_code]

        # %D (Change compared to the previous day)
        stock_data['previous_close'] = stock_data['closing_price'].shift(1)
        stock_data['percent_change_day'] = ((stock_data['closing_price'] - stock_data['previous_close']) / stock_data['previous_close']) * 100

        # %W (Change compared to the previous week)
        stock_data['previous_week_close'] = stock_data.groupby('week')['closing_price'].shift(1)
        stock_data['percent_change_week'] = ((stock_data['closing_price'] - stock_data['previous_week_close']) / stock_data['previous_week_close']) * 100

        # %M (Change compared to the previous month)
        stock_data['previous_month_close'] = stock_data.groupby('month')['closing_price'].shift(1)
        stock_data['percent_change_month'] = ((stock_data['closing_price'] - stock_data['previous_month_close']) / stock_data['previous_month_close']) * 100

        # %Q (Change compared to the previous quarter)
        stock_data['previous_quarter_close'] = stock_data.groupby('quarter')['closing_price'].shift(1)
        stock_data['percent_change_quarter'] = ((stock_data['closing_price'] - stock_data['previous_quarter_close']) / stock_data['previous_quarter_close']) * 100

        # %YTD (Change compared to the beginning of the year)
        first_day_of_year = stock_data[stock_data['trading_date'].dt.month == 1].iloc[0]
        stock_data['percent_change_ytd'] = ((stock_data['closing_price'] - first_day_of_year['closing_price']) / first_day_of_year['closing_price']) * 100

        # %Y (Change compared to the same day last year)
        last_year_same_day = stock_data[stock_data['trading_date'].dt.year == (stock_data['year'].max() - 1)].iloc[0]
        stock_data['percent_change_year'] = ((stock_data['closing_price'] - last_year_same_day['closing_price']) / last_year_same_day['closing_price']) * 100

        # Append the results for the current stock code
        result.append({
            'stock_code': stock_code,
            'Giá': stock_data['closing_price'].iloc[-1],
            '%D': stock_data['percent_change_day'].iloc[-1],
            '%W': stock_data['percent_change_week'].iloc[-1],
            '%M': stock_data['percent_change_month'].iloc[-1],
            '%Q': stock_data['percent_change_quarter'].iloc[-1],
            '%YTD': stock_data['percent_change_ytd'].iloc[-1],
            '%Y': stock_data['percent_change_year'].iloc[-1]
        })

    # Convert the result list to a DataFrame
    result_df = pd.DataFrame(result)

    return result_df

# Example usage:
# Assuming 'latest_index_data' is your original dataframe
# result_df = calculate_percentage_changes(latest_index_data)
# print(result_df)
