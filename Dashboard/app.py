import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

data = {
    "Giá": [1250.46, 224.64, 92.74, 1311.26],
    "%D": ["+0.67%", "+0.48%", "+0.43%", "+0.75%"],
    "%W": ["+1.82%", "+1.51%", "+1.13%", "+1.96%"],
    "%M": ["-0.34%", "+0.02%", "+0.64%", "-1.29%"],
    "%Q": ["-2.42%", "-5.70%", "-1.48%", "-0.93%"],
    "%YTD": ["+10.49%", "-2.33%", "+5.89%", "+15.87%"],
    "%Y": ["+14.15%", "+0.11%", "+9.54%", "+20.46%"],
    "stock_code": ["VN-Index", "HNX", "UPCOM", "VN30"],  # Add stock_code as identifier
}

# Create a DataFrame
df = pd.DataFrame(data)

st.subheader("Chỉ số thị trường")

# Configure the AgGrid table
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection("single", use_checkbox=False)  # Enable single-row selection
grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=300,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme="streamlit",  # Choose from: "streamlit", "light", "dark", "blue", "fresh", "material"
)

if grid_response.get("selected_rows") is not None and not grid_response["selected_rows"].empty:
    selected_row = grid_response["selected_rows"]
    stock_code = selected_row["stock_code"].iloc[0]  # Access the first row's stock_code
    st.success(f"You selected: {stock_code}")
else:
    st.info("No row selected. Please select a row.")