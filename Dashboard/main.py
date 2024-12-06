import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import load_all_tables

from overview_utils import load_css
def setup_page():
 
    st.set_page_config(
        page_title="Stock Market Overview",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded" 
    )
    


# st.title('Ứng dụng Phân tích Chứng khoán')
st.markdown(
    f""" 
        <h1 class="header_style" style="display: inline-block;">Ứng dụng Phân Tích Chứng Khoán</h1>
    """, unsafe_allow_html=True)


st.markdown(
    """
        Chào mừng bạn đến với ứng dụng phân tích chứng khoán của tôi! 
        Ứng dụng này giúp bạn phân tích và theo dõi sự biến động giá cổ phiếu, 
        cung cấp những chỉ số và biểu đồ hỗ trợ ra quyết định đầu tư hiệu quả.
    """)


if "data_frames" not in st.session_state:
    st.session_state["data_frames"] = load_all_tables()
    

st.success("Dữ liệu đã được tải thành công !!!")