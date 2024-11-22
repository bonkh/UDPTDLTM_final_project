import streamlit as st

# CSS để tạo tooltip cho selectbox
tooltip_css = """
    <style>
    /* CSS cho selectbox */
    .streamlit-expanderHeader, .stSelectbox>label {
        position: relative;
    }

    .stSelectbox>label::after {
        content: " ";  /* Chứa nội dung tooltip */
        position: absolute;
        top: -25px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #6c757d;
        color: white;
        border-radius: 5px;
        padding: 8px;
        width: 220px;
        text-align: center;
        visibility: hidden;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }

    .stSelectbox>label:hover::after {
        visibility: visible;
        opacity: 1;
    }
    </style>
"""

# Hiển thị CSS trên Streamlit
st.markdown(tooltip_css, unsafe_allow_html=True)

# Selectbox Streamlit
exchange_filter = st.selectbox(
    "Chọn sàn chứng khoán",  # Label của selectbox
    options=["All", "HOSE", "HNX", "UPCoM"],
    index=0
)

# Hiển thị kết quả
st.write(f"Sàn chứng khoán được chọn: {exchange_filter}")
