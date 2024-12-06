import pandas as pd
import plotly.express as px
import streamlit as st

# Dữ liệu ví dụ cho finance_metric_features_mapping và finance_metric_explanations
finance_metric_features_mapping = {
    'metric1': 'Chỉ số tài chính 1',
    'metric2': 'Chỉ số tài chính 2',
    'metric3': 'Chỉ số tài chính 3'
}

finance_metric_explanations = {
    'Chỉ số tài chính 1': {'description': 'Mô tả về chỉ số tài chính 1', 'insights': 'Các nhận xét về chỉ số tài chính 1'},
    'Chỉ số tài chính 2': {'description': 'Mô tả về chỉ số tài chính 2', 'insights': 'Các nhận xét về chỉ số tài chính 2'},
    'Chỉ số tài chính 3': {'description': 'Mô tả về chỉ số tài chính 3', 'insights': 'Các nhận xét về chỉ số tài chính 3'}
}

# Dữ liệu ví dụ cho filtered_lastest_finance_data và latest_stock_data
filtered_lastest_finance_data = pd.DataFrame({
    'stock_code': ['A', 'B', 'C', 'D', 'E'],
    'metric1': [10, 20, 30, 40, 50],
    'metric2': [50, 40, 30, 20, 10],
    'metric3': [5, 15, 25, 35, 45],
})

latest_stock_data = pd.DataFrame({
    'stock_code': ['A', 'B', 'C', 'D', 'E'],
    'total_trading_volume': [1000, 2000, 1500, 1800, 2200],
    'closing_price': [100, 200, 150, 180, 220],
    'price_change_percentage': [1.5, -2.3, 0.5, -1.0, 3.1],
})

def process_and_display_for_metric(metric_name):
    """Hàm xử lý và hiển thị biểu đồ và bảng cho từng chỉ số tài chính"""
    
    # Lọc cột tương ứng với chỉ số tài chính đã chọn
    criteria_column = [
        key for key, value in finance_metric_features_mapping.items() if value == metric_name
    ][0]
    
    # Kiểm tra dữ liệu có cột không và lọc top 10 cổ phiếu
    if criteria_column in filtered_lastest_finance_data.columns:
        top_10_stocks = filtered_lastest_finance_data.sort_values(by=criteria_column, ascending=False).head(10)

        # Kết hợp với dữ liệu cổ phiếu mới nhất
        merged_top_10_stocks = pd.merge(
            top_10_stocks,
            latest_stock_data[['stock_code', 'total_trading_volume', 'closing_price', 'price_change_percentage']],
            on='stock_code',
            how='left'
        )

        # Hiển thị thông tin mô tả và insights cho chỉ số tài chính
        st.expander(f"{metric_name}").markdown(f"**Mô tả:** {finance_metric_explanations[metric_name]['description']}")
        st.expander(f"{metric_name}").markdown(f"**Insights:** {finance_metric_explanations[metric_name]['insights']}")

        # Hiển thị biểu đồ cột (bar chart)
        fig = px.bar(
            merged_top_10_stocks,
            x='stock_code', 
            y=criteria_column, 
            labels={criteria_column: metric_name, 'stock_code': 'Mã Cổ Phiếu'},
            title=f"Top 10 Cổ Phiếu Theo {metric_name}",
            color=criteria_column,  # Thêm màu sắc cho cột
            color_continuous_scale='Viridis'  # Chọn màu sắc cho biểu đồ
        )
        st.plotly_chart(fig)

        # Hiển thị bảng dữ liệu
        st.dataframe(
            merged_top_10_stocks[['stock_code', 'total_trading_volume', 'closing_price', 'price_change_percentage', criteria_column]].rename(columns={
                "stock_code": "Mã CK",
                "total_trading_volume": "Khối lượng giao dịch",
                "closing_price": "Giá",
                "price_change_percentage": "Thay đổi",
                criteria_column: metric_name,
            })
        )
    else:
        st.warning(f"Dữ liệu không có tiêu chí: {metric_name}")


# Tạo tabs từ finance_metric_features_mapping
tab_names = list(finance_metric_features_mapping.values())
tabs = st.tabs(tab_names)

# Xử lý thủ công mỗi tab được chọn
for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        # Xử lý và hiển thị cho chỉ số tài chính đã chọn
        process_and_display_for_metric(tab_name)
