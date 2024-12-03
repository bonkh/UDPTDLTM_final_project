import streamlit as st
import plotly.express as px
import pandas as pd

# Sample data
df = pd.DataFrame({
    'industry_name': ['Tech', 'Finance', 'Health'],
    'code': ['AAPL', 'GOOGL', 'AMZN'],
    'value': [100, 200, 150],
    'price_change_percentage': [1.5, -2.0, 0.8],
    'color': [1, -1, 0]
})

criteria_mapping = {'value': 'Giá trị giao dịch'}

# Create the Plotly treemap
fig = px.treemap(
    data_frame=df,
    path=['industry_name', 'code'],
    values='value',
    hover_data=['price_change_percentage'],
    color='color',
    color_discrete_map={'-1': '#FF2929', '0': '#F6E96B', '1': '#399918'}
)

# Remove title spacing by setting margin.t = 0
fig.update_layout(
    margin=dict(t=0, l=20, r=20, b=20),
    font=dict(size=10, weight="bold")
)

# Tooltip title with description
tooltip_title = f"""
    <div class="tooltip-title">
        <h3 style="display: inline-block; font-family: Arial, sans-serif; font-size: 24px; color: black; margin: 0;">
            Tổng quan thị trường dựa trên tiêu chí 
            <span style="color: #FF6347;">{criteria_mapping['value']}</span>
        </h3>
        <span class="tooltiptext">
            Biểu đồ này thể hiện tổng quan thị trường dựa trên tiêu chí 
            <span style='color: #FF6347;'><b>{criteria_mapping['value']}</b></span>. 
            <ul>
                <li>Mỗi ô đại diện cho một cổ phiếu.</li>
                <li>Kích thước ô biểu thị giá trị giao dịch.</li>
                <li>Màu sắc cho biết mức tăng/giảm giá so với ngày trước đó.</li>
            </ul>
        </span>
    </div>
"""

# Render tooltip title and set position
st.markdown(
    f"""
    <style>
        .tooltip-title {{

            top: 30px; /* Đặt vị trí so với đỉnh container */
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
            cursor: pointer;
            text-align: center;
        }}

        .tooltip-title .tooltiptext {{
            visibility: hidden;
            width: 350px;
            background-color: #f9f9f9;
            color: #333;
            text-align: left;
            border-radius: 5px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            top: 120%; 
            left: 50%;
            transform: translateX(-50%);
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            font-size: 14px;
            font-family: Arial, sans-serif;
        }}

        .tooltip-title:hover .tooltiptext {{
            visibility: visible;
        }}

        .stPlotlyChart {{
            position: relative;
        }}
    </style>

    {tooltip_title}
    """,
    unsafe_allow_html=True,
)

# Display the Plotly chart
st.plotly_chart(fig, use_container_width=True)
