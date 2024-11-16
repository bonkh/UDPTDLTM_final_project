import streamlit as st
import pandas as pd
import plotly.express as px

# Sample DataFrame
stock_info = pd.DataFrame({
    'industry_name': ['Industry1', 'Industry2', 'Industry1', 'Industry2'],
    'code': ['CodeA', 'CodeB', 'CodeC', 'CodeD'],
    'total_trading_value': [1000, 1500, 500, 800],
    'price_change_percentage': [5.2, -3.1, 2.0, -1.5],
    'exchange': ['HOSE', 'HNX', 'UPCOM', 'HOSE']
})

# Create a treemap
fig = px.treemap(
    stock_info,
    path=['industry_name', 'code'],
    values='total_trading_value',
    color='price_change_percentage',
    color_continuous_scale='RdYlGn'
)

# Streamlit Plotly event capture for click interaction
selected_code = st.session_state.get("selected_code", None)

def update_code_on_click(trace, points, selector):
    if points.point_inds:
        selected_code = points.hovertext  # hovertext contains 'code' for this example
        st.session_state.selected_code = selected_code

# Display treemap
st.plotly_chart(fig, use_container_width=True)

# Display stock details if a code is selected
if selected_code:
    stock_details = stock_info[stock_info['code'] == selected_code]
    st.write(f"Details for {selected_code}:")
    st.table(stock_details)
