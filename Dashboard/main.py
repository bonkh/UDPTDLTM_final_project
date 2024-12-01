import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import load_all_tables

from overview_utils import load_css

def setup_page():
    # Thiết lập cấu hình trang Streamlit
    st.set_page_config(
        page_title="Stock Market Overview",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded" 
    )
    
    # Tiêu đề ứng dụng
    st.title('Ứng dụng Phân tích Chứng khoán')

# Mô tả ngắn về ứng dụng
st.markdown("""
Chào mừng bạn đến với ứng dụng phân tích chứng khoán của tôi! 
Ứng dụng này giúp bạn phân tích và theo dõi sự biến động giá cổ phiếu, 
cung cấp những chỉ số và biểu đồ hỗ trợ ra quyết định đầu tư hiệu quả.
""")


if "data_frames" not in st.session_state:
    st.session_state["data_frames"] = load_all_tables()
    
# Thông báo khi dữ liệu đã được tải
st.success("Dữ liệu đã được tải thành công !!!")