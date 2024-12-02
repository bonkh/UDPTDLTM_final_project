import streamlit as st
from streamlit.components.v1 import html

# Tooltip content stored in a dictionary
tooltip_dict = {
    "stock_exchange_explanation": """
        <p>Sàn chứng khoán là nơi mà các chứng khoán như cổ phiếu, trái phiếu được giao dịch. Hiện nay, ở Việt Nam đang có ba sàn chứng khoán chính sau:</p>
        <ul>
            <li>HOSE: Sở Giao dịch Chứng khoán TP.HCM</li>
            <li>HNX: Sở Giao dịch Chứng khoán Hà Nội</li>
            <li>UPCoM: Thị trường giao dịch cổ phiếu của các công ty chưa niêm yết trên sàn chứng khoán chính thức.</li>
        </ul>
        <p>Mỗi sàn có những đặc điểm và danh sách cổ phiếu riêng biệt. Chọn tất cả hoặc từng sàn để xem các cổ phiếu giao dịch tại đó.</p>
    """
}

# Tooltip HTML structure with CSS
tooltip_html = f"""
    <style>
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: pointer;
        }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 300px;
            background-color: black;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -150px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
    </style>

    <div class="tooltip">
        Chọn sàn chứng khoán
        <span class="tooltiptext">
            {tooltip_dict["stock_exchange_explanation"]}
        </span>
    </div>
"""

# Use Streamlit's HTML renderer for full control
html(tooltip_html, height=250)
