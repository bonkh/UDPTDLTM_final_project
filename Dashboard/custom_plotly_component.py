import streamlit.components.v1 as components

# Định nghĩa component tùy chỉnh
def custom_plotly_component():
    # Chỉ định đường dẫn đến thư mục chứa plotly_hover.js
    return components.declare_component("plotly_hover", path="./custom_component")
