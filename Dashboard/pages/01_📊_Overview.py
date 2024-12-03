import os
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from overview_utils import display_index_overview, criteria_english, criteria_mapping, display_stock_overview, column_explanations, load_css, remove_html_tags, tooltip_dict, finance_metric_features_mapping, calculate_percentage_changes
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from data_loader import load_all_tables
from datetime import datetime, date, timedelta
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

load_css("styles/tooltip_style.css")

if "data_frames" not in st.session_state:
    st.session_state["data_frames"] = load_all_tables()
    

data_frames = st.session_state["data_frames"]
stock_data = data_frames.get("stock_data", pd.DataFrame())
stock_info = data_frames.get("stock_info", pd.DataFrame())
stock_index = data_frames.get("stock_index", pd.DataFrame())
stock_financial_metrics = data_frames.get("financial_metrics", pd.DataFrame())

st.markdown(
    f"""
        <div class="tooltip tooltip-right">
            <h3 class="header_style" style="display: inline-block;">TỔNG QUAN THỊ TRƯỜNG</h3>
            <span class="tooltiptext">
                {tooltip_dict['market_overview_page']}
            </span>
        </div>
    """, unsafe_allow_html=True)


stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'], errors='coerce')
stock_data = stock_data.sort_values(by='trade_date').reset_index(drop=True)
latest_date = stock_data['trade_date'].max()

one_month_before = latest_date - timedelta(days=30)

st.markdown(
    f"""
        <div class="tooltip tooltip-right">
            <h3>Ngày: </h3>
            <span class="tooltiptext">
                {tooltip_dict['up_to_date']}
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

# st.write(end_date)
end_date_datetime = datetime.combine(end_date, datetime.min.time())
# st.write(end_date_datetime)

info_col, chart_col = st.columns([1, 3]) 

with chart_col:
    col1, col2, col3 = st.columns(3)

    with col1:
        
        st.markdown(
            f"""
                <div class="tooltip" style="font-weight: bold">
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
            """,unsafe_allow_html=True)

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
            f"""
                <div class="tooltip" style="font-weight: bold">
                Chọn ngành
                    <span class="tooltiptext"> 
                            {tooltip_dict['industry_explaination']}
                    </span>
                </div>
            """,
            unsafe_allow_html=True,)

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
        f"""
            <div class="tooltip" style="font-weight: bold">
            Chọn tiêu chí so sánh
                <span class="tooltiptext">
                    {tooltip_dict["zone_size_explaination"]}
                </span>
            </div>
        """, unsafe_allow_html=True)

        zone_size_feature = st.selectbox(
            "Select zone size",
            options=[criteria_mapping[criterion][0] for criterion in criteria_english],
            index = 5 ,
            label_visibility="collapsed"
        )

    zone_size_feature = [key for key, value in criteria_mapping.items() if zone_size_feature in value][0]

    latest_stock_data = stock_data[stock_data['trade_date'] == end_date_datetime]
    latest_stock_selected_feature_data = latest_stock_data[['stock_code', zone_size_feature]]

    merged_data = pd.merge(filtered_stock_info, latest_stock_selected_feature_data, left_on='code', right_on='stock_code', how='inner')

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

    st.markdown(
        f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 20px;">
                <div class="tooltip">
                    <h3 style=" color: #333;">Biểu đồ cơ cấu thị trường</h3>
                    <span class="tooltiptext">
                        Biểu đồ này thể hiện tình hình thị trường dựa trên tiêu chí <span style='color: #FF6347;'><b>{criteria_mapping[zone_size_feature][0]}</b></span>. 
                        <ul style="list-style-type: none; padding: 0; text-align: left;">
                            <li>Mỗi ô đại diện cho một cổ phiếu.</li>
                            <li>Kích thước ô biểu thị giá trị của tiêu chí đã chọn.</li>
                            <li>Màu sắc cho biết mức tăng/giảm giá so với ngày trước đó.</li>
                        </ul>
                        {criteria_mapping[zone_size_feature][1]}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True
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
        # title=f"<b>Tổng quan thị trường dựa trên tiêu chí <span style='font-family: Arial, sans-serif; color: #FF6347;'>{criteria_mapping[zone_size_feature]}</span></b>", 
        # title_font=dict(family="Arial", size=20, weight="bold", color="black"),
        margin=dict(t=0, l=20, r=20, b=20),
        font=dict(size=10, weight="bold"),

        plot_bgcolor='white',
        paper_bgcolor='lightgrey',

    )
    updated_labels = ['<b>' + label + '</b>' for label in market_overview_fig.data[0].labels]
    # updated_labels = [
    # f'<b><span style="{"font-family= Roboto, sans-serif"}">{label}</span></b>' 
    # for label in market_overview_fig.data[0].labels]

    # Update the figure with the modified labels
    market_overview_fig.data[0].labels = updated_labels

    criterion_name = criteria_mapping[zone_size_feature][0]

    market_overview_fig.update_traces(
        hovertemplate = (
        f"Cổ phiếu của doanh nghiệp <b>%{{label}}</b> <br> "
        f"{criterion_name} hiện tại là <b>%{{value}}</b> <br>"
        "Giá cổ phiếu so với ngày hôm trước có sự biến động là <b><i>%{customdata[1]:.2f}%</i></b>"
        ),

        hoverlabel=dict(
            font_size=20,  
            font_color="black"
        ),

     
    )


    market_overview_fig.data[0].texttemplate = "%{label}<br><b>%{customdata[1]:.2f}%</b>"
    market_overview_fig.data[0].textfont = dict(size=15, weight="bold", color="black")  # Change color to black
    market_overview_fig.data[0].textposition = "middle center"



    colors_list = list(market_overview_fig.data[0]['marker']['colors'])
    colors_list = ['#ECEBDE' if color  == '#000004' else color for color in colors_list]
    market_overview_fig.data[0]['marker']['colors'] = tuple(colors_list)

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
                hovered_label = remove_html_tags(hovered_label)
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


st.markdown(
    f"""
        <div class="tooltip tooltip-right">
            <h3>Biến động của các chỉ số Index </h3>
            <span class="tooltiptext">
                {tooltip_dict['stock_index_change']}
            </span>
        </div>
    """, unsafe_allow_html=True)
st.subheader("Biến động của các chỉ số Index")

col_1, col_2  = st.columns(2) 

selected_index_stock_code = ""
with col_2:
    stock_index['trading_date'] = pd.to_datetime(stock_index['trading_date'], errors='coerce')
    stock_index = stock_index.sort_values(by='trading_date').reset_index(drop=True)
    latest_stock_index_date = stock_index['trading_date'].max()
    # latest_index_data = stock_index[stock_index['trading_date'] == latest_stock_index_date]

    latest_index_data = calculate_percentage_changes(stock_index)

    

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
    time_period_options = ["5D", "1M", "3M", "6M", "YTD", "1Y", "ALL"]
    selected_period_label = st.radio("Lựa chọn khoảng thời gian", time_period_options, horizontal=True, label_visibility="collapsed")

    # Map the selected time period to days
    time_delta_mapping = {
        "5D": 5,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "YTD": pd.Timestamp.today().day_of_year,  # Từ đầu năm đến hiện tại
        "1Y": 365,
        "ALL": None  # No time limit
    }

    # Get the corresponding days for the selected period
    selected_period = time_delta_mapping[selected_period_label]

    # Calculate the start and end date
    end_date = pd.Timestamp.today()

    # Handle the start date based on selected period
    if selected_period is None:  # Trường hợp ALL
        start_date = stock_index['trading_date'].min()  # Lấy giá trị nhỏ nhất từ dữ liệu
    else:
        start_date = end_date - pd.Timedelta(days=selected_period)

    # Ensure 'trading_date' is in datetime format
    stock_index['trading_date'] = pd.to_datetime(stock_index['trading_date'])

    # Filter the data for the selected period and stock code
    index_data = stock_index[(stock_index['stock_code'] == selected_index_stock_code) & 
                            (stock_index['trading_date'] >= start_date)]

    # Sort the data by trading_date
    index_data = index_data.sort_values(by='trading_date').reset_index(drop=True)

    # Plot the data using Plotly
    index_fig = px.line(
        index_data,
        x='trading_date', 
        y='closing_price', 
        color='stock_code',
        labels={'closing_price': 'Giá đóng cửa', 'trading_date': 'Ngày giao dịch'}
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
lastest_date = stock_financial_metrics['date'].max()
lastest_finance_data = stock_financial_metrics[stock_financial_metrics['date'] == lastest_date]

st.table(lastest_finance_data.head())
# top_10_stock = stock_data[['stock_code', 'market_capitalization', 'closing_price', 'price_change', 'price_change_percentage']]
# top_10_stock['price_change'] = top_10_stock['price_change'].apply(lambda x: f"{x} ({top_10_stock['price_change_percentage']}%)")
# top_10_stock = top_10_stock.sort_values(by='market_capitalization', ascending=False).reset_index(drop=True)


metrics = {
"P/E": "pe",
"P/B": "pb",
"EPS": "eps",
}

# # Create tabs dynamically
# tabs = st.tabs(list(metrics.keys()))

# # Populate each tab with data
# for tab, (tab_name, column) in zip(tabs, metrics.items()):
#     with tab:
#         sorted_data = lastest_finance_data.sort_values(by=column, ascending=False).head(10)
#         st.table(sorted_data.head())

col1, col2 = st.columns(2)


with col1:
    st.markdown("Top 10 cổ phiếu")

    tabs = st.tabs(list(finance_metric_features_mapping.values())[0:4])

    for tab_name, tab in zip(finance_metric_features_mapping.values(), tabs):
        with tab:
            # Chuyển từ tên tiếng Việt sang tiếng Anh
            criteria_column = [
                key for key, value in finance_metric_features_mapping.items() if value == tab_name
            ][0]

            # Kiểm tra dữ liệu có cột không
            if criteria_column in lastest_finance_data.columns:
     
                top_10_stocks = ( lastest_finance_data.sort_values(by=criteria_column, ascending=False).head(10))

                merged_top_10_stocks = pd.merge(
                    top_10_stocks,
                    latest_stock_data[['stock_code', 'total_trading_volume', 'closing_price', 'price_change_percentage']],  # Columns from latest_stock_data
                    on='stock_code',
                    how='left'
                )

                st.write(
                    merged_top_10_stocks[['stock_code', 'total_trading_volume', 'closing_price', 'price_change_percentage', criteria_column]].rename(columns={
                        "stock_code": "Mã CK",
                        "total_trading_volume": "Khối lượng giao dịch",
                        "closing_price": "Giá", 
                        "price_change_percentage": "Thay đổi", 
                        criteria_column: tab_name,
                    })
                )

            else:
                st.warning(f"Dữ liệu không có tiêu chí: {tab_name}")


with col2:
    st.markdown("Top 10 theo chỉ số")
    tabs = st.tabs(list(finance_metric_features_mapping.values())[4:])

    for tab_name, tab in zip(finance_metric_features_mapping.values(), tabs):
        with tab:
            # Chuyển từ tên tiếng Việt sang tiếng Anh
            criteria_column = [
                key for key, value in finance_metric_features_mapping.items() if value == tab_name
            ][0]

            # Kiểm tra dữ liệu có cột không
            if criteria_column in lastest_finance_data.columns:
     
                top_10_stocks = ( lastest_finance_data.sort_values(by=criteria_column, ascending=False).head(10))

                merged_top_10_stocks = pd.merge(
                    top_10_stocks,
                    latest_stock_data[['stock_code', 'total_trading_volume', 'closing_price', 'price_change_percentage']],  # Columns from latest_stock_data
                    on='stock_code',
                    how='left'
                )

                st.write(
                    merged_top_10_stocks[['stock_code', 'total_trading_volume', 'closing_price', 'price_change_percentage', criteria_column]].rename(columns={
                        "stock_code": "Mã CK",
                        "total_trading_volume": "Khối lượng giao dịch",
                        "closing_price": "Giá", 
                        "price_change_percentage": "Thay đổi", 
                        criteria_column: tab_name,
                    })
                )

            else:
                st.warning(f"Dữ liệu không có tiêu chí: {tab_name}")
