import streamlit as st
# Set up page configuration
st.set_page_config(
    page_title="Stock Dashboard đó",
    layout="wide", 
)
import importlib
import os
from data_loader import load_all_tables

from PTDLTM.Project.Chatbot.UDPTDLTM_final_project.Dashboard.overview_utils import load_css

PAGES = {
    "Overview": {
        "module": "overview_page",
        "tooltip": "The Overview page provides a summary of all stocks, including performance trends and overall market analysis.",
    },
    "Detail": {
        "module": "detail_page",
        "tooltip": "The Detail page allows in-depth analysis of individual stocks with financial metrics and predictions.",
    },
    "Chatbot": {
        "module": "chat_bot",
        "tooltip": "Chat bot hỗ trợ tra cứu và tìm hiểu thông tin của cổ phiếu dựa trên dữ liệu báo chí"
    }
}

if "data_frames" not in st.session_state:
    st.session_state["data_frames"] = load_all_tables()


load_css("tooltip_style.css")

st.sidebar.title("Chọn trang bạn muốn xem")

with st.sidebar:
    for page, info in PAGES.items():
        rectangle_html = f"""
        <div class="tooltip tooltip-right" style="margin-bottom: 10px; width: 100%; text-align: center;">
            <a href="/?page={info['module']}" target="_self" style="
                display: inline-block;
                width: 100%;
                padding: 15px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            ">{page}</a>
            <span class="tooltiptext ">{info['tooltip']}</span>
        </div>
        """
        st.markdown(rectangle_html, unsafe_allow_html=True)


selected_module = st.query_params.get("page", PAGES["Overview"]["module"])


if selected_module in [info["module"] for info in PAGES.values()]:
    page_module = importlib.import_module(selected_module)

    if hasattr(page_module, "render"):
        page_module.render()
    else:
        st.error(f"The selected page '{selected_module}' is missing a render() function.")
else:
    st.error("Invalid page selection.")
