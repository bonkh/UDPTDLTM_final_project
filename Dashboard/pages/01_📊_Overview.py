import streamlit as st
from streamlit_plotly_events import plotly_events
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from overview_utils import get_filtered_data, display_index_overview, criteria_english, criteria_mapping, display_stock_overview, column_explanations, load_css
import time 
import datetime
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from dotenv import load_dotenv

load_dotenv()

conn_str = os.getenv('DATABASE_RENDER')
def setup_page():
    st.set_page_config(
        page_title="Overview Trading Market",
        page_icon="📊",
        layout="wide",
    )

setup_page()

custom_css = """
    <style>
        .main {
            margin: 20px 40px;  /* Top-Bottom: 20px, Left-Right: 40px */
        }
        .block-container {
            padding: 2rem 4rem;  /* Adjust inner padding */
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

st.markdown(
    """
    <style>
        .selectbox-label {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)



# def render():
load_css("styles/tooltip_style.css")

data_frames = st.session_state["data_frames"]
stock_data = data_frames.get("stock_data", pd.DataFrame())
stock_info = data_frames.get("stock_info", pd.DataFrame())
stock_index = data_frames.get("stock_index")
stock_financial_metrics = data_frames.get("financial_metrics")




st.markdown("""
<div class="tooltip tooltip-right">
    <h3 style="display: inline-block;">Tổng quan thị trường</h3>
    <span class="tooltiptext">
        Trang này cung cấp thông tin tổng quan về thị trường, bao gồm các chỉ số chính, xu hướng và biến động.
    </span>
</div>
""", unsafe_allow_html=True)


stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'], errors='coerce')
stock_data = stock_data.sort_values(by='trade_date').reset_index(drop=True)
latest_date = stock_data['trade_date'].max()

one_month_before = latest_date - datetime.timedelta(days=30)

# Tạo danh sách các ngày từ hôm nay đến một tháng sau
date_options = [latest_date - datetime.timedelta(days=i) for i in range(0, 31)]

# Hiển thị phần markdown và date_input trên cùng một dòng
st.markdown("""
    <div class="tooltip tooltip-right">
        <h3>Đến ngày: </h3>
        <span class="tooltiptext">
            Chọn ngày cuối cùng mà thông tin về thị trường được tổng hợp, việc xem xét tổng quan thị trường trên nhiều ngày khác nhau sẽ đem đến sự so sánh về những biến đổi trên thị trường qua nhiều ngày
        </span>
    </div>
""", unsafe_allow_html=True)

end_date = st.date_input(
    "Chọn ngày", 
    value=latest_date, 
    min_value=one_month_before, 
    max_value=latest_date,
    label_visibility="collapsed"
)


info_col, chart_col = st.columns([1, 3]) 

with chart_col:
    col1, col2, col3 = st.columns(3)

    with col1:
        
        st.markdown(
            """
            <div class="tooltip">
            Chọn sàn chứng khoán
            <span class="tooltiptext">
                Sàn chứng khoán là nơi mà các chứng khoán như cổ phiếu, trái phiếu được giao dịch. Hiện nay, ở Việt Nam đang có ba sàn chứng khoán chính sau:
                <ul>
                    <li>HOSE: Sở Giao dịch Chứng khoán TP.HCM</li>
                    <li>HNX: Sở Giao dịch Chứng khoán Hà Nội </li>
                    <li>UPCoM: Thị trường giao dịch cổ phiếu của các công ty chưa niêm yết trên sàn chứng khoán chính thức.</li>
                </ul>
                Mỗi sàn có những đặc điểm và danh sách cổ phiếu riêng biệt. Chọn tất cả hoặc từng sàn để xem các cổ phiếu giao dịch tại đó.
            </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        exchange_filter = st.selectbox(
            "exchange",
            options=["All", "HOSE", "HNX", "UPCoM"],
            index=0,
            label_visibility="collapsed"
        )

        if "All" in exchange_filter:
    
            filtered_stock_info = stock_info
        else:

            filtered_stock_info = stock_info[stock_info['exchange'] == exchange_filter]

    with col2:

        st.markdown(
        """
        <div class="tooltip">
        Chọn ngành
        <span class="tooltiptext"> 
        Lựa chọn ngành kinh tế mà bạn muốn xem, có thể là bất kỳ ngành nào từ danh sách các ngành hiện có.
        Các mã chứng khoán sẽ được nhóm theo ngành tương ứng của chúng để dễ dàng so sánh và phân tích.</span>
        </div>
        """,
        unsafe_allow_html=True,
        )

        industry_filter = st.selectbox(
            "industry",
            options=['All'] + list(stock_info['industry_name'].unique()),
            index = 0 ,
            label_visibility="collapsed"
        )

        if "All" not in industry_filter:
            filtered_stock_info = filtered_stock_info[filtered_stock_info['industry_name'] == industry_filter]

    
    with col3:
        st.markdown(
        """
        <div class="tooltip">
        Chọn tiêu chí so sánh
        <span class="tooltiptext">Các cổ phiếu sẽ được hiển thị với kích thước dựa trên tiêu chí này.
        Các tiêu chí này có thể bao gồm vốn hóa thị trường, giao dịch hàng ngày, hoặc bất kỳ tiêu chí nào phù hợp với nhu cầu phần tích của bạn.
        Ở đây, tiêu chí mặc định sẽ là tổng khối lượng giao dịch trong ngày.</span>
        </div>
        """,
        unsafe_allow_html=True,
        )
        zone_size_feature = st.selectbox(
            "Select zone size",
            options=[criteria_mapping[criterion] for criterion in criteria_english],
            index = 5 ,
            label_visibility="collapsed"
        )

    zone_size_feature = [key for key, value in criteria_mapping.items() if value == zone_size_feature][0]
    latest_data = stock_data[stock_data['trade_date'] == latest_date][['stock_code', zone_size_feature]]

    merged_data = pd.merge(filtered_stock_info, latest_data, left_on='code', right_on='stock_code', how='inner')

    latest_price_change = stock_data.sort_values('trade_date').drop_duplicates('stock_code', keep='last')
    latest_price_change = latest_price_change[['stock_code', 'price_change_percentage']]
    merged_data = pd.merge(merged_data, latest_price_change, left_on='code', right_on='stock_code', how='left')
    merged_data = merged_data.dropna(subset=['price_change_percentage'])


    industry_totals = merged_data.groupby('industry_name')[zone_size_feature].sum().reset_index()
    industry_totals = industry_totals.rename(columns={f'{zone_size_feature}': f'industry_{zone_size_feature}'})

    
    top_bottom_df = pd.merge(merged_data, industry_totals, on='industry_name')


    top_bottom_df['color'] = top_bottom_df['price_change_percentage'].apply(
        lambda x: '0' if x == 0 else ('1' if x > 0 else '-1')
    )

    market_overview_fig = px.treemap(
        data_frame=top_bottom_df,
        path=['industry_name', 'code'], 
        values=zone_size_feature, 
        hover_data=[zone_size_feature, 'price_change_percentage'], 
        hover_name='code',
        color='color',
        color_discrete_map={'-1': '#FF2929', '0': '#F6E96B', '1': '#399918'}
    )

    market_overview_fig.update_layout(
        margin=dict(t=50, l=20, r=20, b=20),
        font=dict(size=10, weight="bold"),
    )

    market_overview_fig.data[0].texttemplate = "%{label}<br><b>%{customdata[1]:.2f}%</b>"
    market_overview_fig.data[0].textfont = dict(size=15, weight="bold", color="black")  # Change color to black
    market_overview_fig.data[0].textposition = "middle center"



    colors_list = list(market_overview_fig.data[0]['marker']['colors'])
    colors_list = ['white' if color  == '#000004' else color for color in colors_list]
    market_overview_fig.data[0]['marker']['colors'] = tuple(colors_list)

    # st.write(market_overview_fig.data[0])
    
    hover_data = plotly_events(market_overview_fig, click_event=True,select_event = False, hover_event=False)

    with info_col:

        stock_index['trading_date'] = pd.to_datetime(stock_index['trading_date'], errors='coerce')
        stock_index = stock_index.sort_values(by='trading_date').reset_index(drop=True)

        vn_index_data = stock_index[stock_index['stock_code'] == 'VN-Index']
        hnx_index_data = stock_index[stock_index['stock_code'] == 'HNX-Index']
        upcom_index_data = stock_index[stock_index['stock_code'] == 'UPCOM-Index']

        vn_index_data = vn_index_data.sort_values(by="trading_date", ascending=False).reset_index(drop=True)

        display_index_overview(vn_index_data, "VN-Index", "VN-Index", "HOSE")
        display_index_overview(hnx_index_data, "HNX-Index", "HNX-Index", "HNX")
        display_index_overview(upcom_index_data, "UPCOM-Index", "UPCOM-Index", "UPCOM")
        st.markdown("---")



    if hover_data:

        
        point_number = hover_data[0].get('pointNumber', None) 

        if point_number:

            labels = market_overview_fig.data[0]['labels']
            if labels not in market_overview_fig.data[0]['parents']:
        
                hovered_label = labels[point_number]
                with info_col:
                    with st.container():
                        if hovered_label in stock_data['stock_code'].unique():
                            selected_row = stock_data[stock_data['stock_code'] == hovered_label].iloc[0]

                            st.subheader(f"Mã cổ phiếu: {selected_row['stock_code']}")

                            name = stock_info[stock_info['code'] == hovered_label]['name'].iloc[0]
                            st.markdown(name)

                            industry = stock_info[stock_info['code'] == hovered_label]['industry_name'].iloc[0]
                            st.markdown(industry)

                            columns_to_select = [
                                "market_capitalization", "reference_price", "ceiling_price", "floor_price",
                                "opening_price", "closing_price", "highest_price", "lowest_price",
                                "total_trading_volume", "total_trading_value"
                            ]

    
                            selected_row = stock_data.loc[stock_data['stock_code'] == hovered_label, columns_to_select].iloc[0]

                            for column, value in selected_row.items():
                    
                                if isinstance(value, float):
                                    value = f"{value:.2f}"

                                tooltip_text = (
                                    f"Đây là cột {criteria_mapping[column]}, {column_explanations[column]}"
                                    f"Giá trị hiện tại trong ngày {latest_date} là {value}."
                                )
                                st.markdown(
                                    f"""
                                    <div class="tooltip tooltip-right "  style="display: flex; align-items: center; justify-content: space-between; white-space: nowrap;">
                                        <div style="font-size: 15px; font-weight: bold; text-align: left; margin-right: 10px;">
                                            {criteria_mapping[column]}:
                                        </div>
                                        <div style="font-size: 15px; text-align: right;">
                                            {value}
                                        </div>
                                        <span class="tooltiptext">
                                        {tooltip_text}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                    )
                        else:
                            st.write(f"Industry: {hovered_label}")


st.subheader("Biến động của các chỉ số Index")

col_1, col_2  = st.columns(2) 

selected_index_stock_code = ""
with col_2:
    stock_index['trading_date'] = pd.to_datetime(stock_index['trading_date'], errors='coerce')
    stock_index = stock_index.sort_values(by='trading_date').reset_index(drop=True)
    latest_stock_index_date = stock_index['trading_date'].max()
    latest_index_data = stock_index[stock_index['trading_date'] == latest_stock_index_date]

    st.table(latest_index_data)

    gb = GridOptionsBuilder.from_dataframe(latest_index_data)
    gb.configure_selection("single", use_checkbox=False)  # Enable single-row selection
    grid_options = gb.build()

    grid_response = AgGrid(
        latest_index_data,
        gridOptions=grid_options,
        height=300,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit",  # Choose from: "streamlit", "light", "dark", "blue", "fresh", "material"
    )

    if grid_response.get("selected_rows") is not None and not grid_response["selected_rows"].empty:
        selected_row = grid_response["selected_rows"]
        selected_index_stock_code = selected_row["stock_code"].iloc[0]  # Access the first row's stock_code
    else:
        st.info("No row selected. Please select a row.")
    

    
with col_1:
    st.subheader("Biến động của các chỉ số Index")

    time_period_tabs = st.tabs(["1D", "5D", "1M", "3M", "6M", "YTD", "1Y", "ALL"])
    
    # Gán giá trị thời gian tương ứng với mỗi tab
    time_delta_mapping = {
        "1D": 1,
        "5D": 5,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "YTD": pd.Timestamp.today().day_of_year,  # Từ đầu năm đến hiện tại
        "1Y": 365,
        "ALL": None  # Không giới hạn thời gian
    }
    
    for tab, (label, days) in zip(time_period_tabs, time_delta_mapping.items()):
        with tab:
            st.write(f"Lựa chọn khoảng thời gian: {label}")
            selected_period = days

    # Xác định khoảng thời gian bắt đầu và kết thúc
    end_date = pd.Timestamp.today()
    if selected_period is None:  # Trường hợp ALL
        start_date = stock_index['trading_date'].min()  # Lấy giá trị nhỏ nhất từ dữ liệu
    else:
        start_date = end_date - pd.Timedelta(days=selected_period)
    

    stock_index = stock_index.sort_values(by='trading_date').reset_index(drop=True)
    
    
    index_data = stock_index[(stock_index['stock_code'] == selected_index_stock_code) & 
                            (stock_index['trading_date'] >= start_date)]
    
    # Vẽ biểu đồ
    index_fig = px.line(
        index_data,
        x='trading_date', 
        y='closing_price', 
        color='stock_code',
        labels={'closing_price': 'Giá đóng cửa', 'trade_date': 'Ngày giao dịch'}
    )
    st.plotly_chart(index_fig, use_container_width=True)




st.subheader("Top cổ phiếu ảnh hưởng đến chỉ số chứng khoán của sàn")

st.markdown(
            """
            <div class="tooltip tooltip-right">
            Chọn sàn chứng khoán
            </div>
            """,
            unsafe_allow_html=True,
        )
exchange = st.selectbox(
            "exchange",
            options=["All", "HOSE", "HNX", "UPCoM"],
            index=0,
            label_visibility="collapsed",
            key="selectbox_exchange"
        )

if "All" in exchange:

    filtered_stock_info = stock_info
else:

    filtered_stock_info = stock_info[stock_info['exchange'] == exchange]

latest_market_data =  stock_data[stock_data['trade_date'] == latest_date][['stock_code', 'market_capitalization', 'price_change_percentage']]
merged_data = pd.merge(filtered_stock_info, latest_market_data, left_on='code', right_on='stock_code', how='inner')

# st.table(merged_data.head())

total_market_cap = merged_data['market_capitalization'].sum()

merged_data['weight'] = merged_data['market_capitalization'] / total_market_cap

merged_data['impact_on_index'] = merged_data['weight'] * merged_data['price_change_percentage']

vn_index_data = merged_data.sort_values(by='impact_on_index', ascending=False)

top_positive = vn_index_data.sort_values(by='impact_on_index', ascending=False).head(10)
top_negative = vn_index_data.sort_values(by='impact_on_index').head(10)
filtered_data = pd.concat([top_positive, top_negative])

# Add color column based on impact direction
filtered_data['color'] = filtered_data['impact_on_index'].apply(lambda x: 'green' if x > 0 else 'red')

impact_on_vn_index_fig = px.bar(
    filtered_data,
    x='stock_code',
    y='impact_on_index',
    color='color',
    labels={'impact_on_index': 'Độ ảnh hưởng', 'stock_code': 'Mã cổ phiếu'},
    color_discrete_map={'green': 'green', 'red': 'red'}
)

# Customize layout
impact_on_vn_index_fig.update_layout(
    xaxis_title="Mã cổ phiếu ",
    yaxis_title="Tác động đến chỉ số index",
    showlegend=False,
    margin=dict(t=50, l=25, r=25, b=25)
)

st.plotly_chart(impact_on_vn_index_fig, use_container_width=True)



st.subheader("Top 10 cổ phiếu theo chỉ số")

stock_financial_metrics['date'] = pd.to_datetime(stock_financial_metrics['date'], errors='coerce')
stock_financial_metrics = stock_financial_metrics.sort_values(by='date').reset_index(drop=True)
# st.table(stock_financial_metrics.head(10))


latest_date = stock_financial_metrics['date'].max()
latest_finance_data = stock_financial_metrics[stock_financial_metrics['date'] == latest_date]

top_10_stock = stock_data[['stock_code', 'market_capitalization', 'closing_price', 'price_change', 'price_change_percentage']]
top_10_stock['price_change'] = top_10_stock['price_change'].apply(lambda x: f"{x} ({top_10_stock['price_change_percentage']}%)")
top_10_stock = top_10_stock.sort_values(by='market_capitalization', ascending=False).reset_index(drop=True)




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

    # col1, col2 = st.columns(2)


    # with col1:
    #     st.markdown("Top 10 cổ phiếu")

    #     tab = st.radio("Chọn tab", ["Tab 1", "Tab 2", "Tab 3"])

    #     if tab == "Tab 1":
    #         st.write("Nội dung của Tab 1")
    #     elif tab == "Tab 2":
    #         st.write("Nội dung của Tab 2")
    #     else:
    #         st.write("Nội dung của Tab 3")
    #     # st.table(top_10_stock)


    # with col2:
    #     st.markdown("Top 10 theo chỉ số")
    #     # st.table(top_10_index)
        
    # stock_financial_metrics['date'] = pd.to_datetime(stock_financial_metrics['date'], errors='coerce')
    # stock_financial_metrics = stock_financial_metrics.sort_values(by='date').reset_index(drop=True)
    # # st.table(stock_financial_metrics.head(10))


    # latest_date = stock_financial_metrics['date'].max()
    # latest_finance_data = stock_financial_metrics[stock_financial_metrics['date'] == latest_date]

    # top_10_stock = stock_data[['stock_code', 'market_capitalization', 'closing_price', 'price_change', 'price_change_percentage']]
    # top_10_stock['price_change'] = top_10_stock['price_change'].apply(lambda x: f"{x} ({top_10_stock['price_change_percentage']}%)")
    # top_10_stock = top_10_stock.sort_values(by='market_capitalization', ascending=False).reset_index(drop=True)




    # metrics = {
    # "P/E": "pe",
    # "P/B": "pb",
    # "EPS": "eps",
    # }

    # # Create tabs dynamically
    # # tabs = st.tabs(list(metrics.keys()))

    # # Populate each tab with data
    # # for tab, (tab_name, column) in zip(tabs, metrics.items()):
    # #     with tab:
    # #         sorted_data = latest_finance_data.sort_values(by=column, ascending=False).head(10)
    # #         st.table(sorted_data)

    # col1, col2 = st.columns(2)


    # with col1:
    #     st.markdown("Top 10 cổ phiếu")

    #     tab = st.radio("Chọn tab", ["Tab 1", "Tab 2", "Tab 3"])

    #     if tab == "Tab 1":
    #         st.write("Nội dung của Tab 1")
    #     elif tab == "Tab 2":
    #         st.write("Nội dung của Tab 2")
    #     else:
    #         st.write("Nội dung của Tab 3")
    #     # st.table(top_10_stock)


    # with col2:
    #     st.markdown("Top 10 theo chỉ số")
    #     # st.table(top_10_index)