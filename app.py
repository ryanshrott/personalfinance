import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder, GridUpdateMode
from utils import *
import math
import requests


st.set_page_config(page_title="💸 Portfolio Rebalancing App 💸", page_icon=":guardsman:", layout="wide")

from streamlit.components.v1 import html

button = """
<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="ryanshrott" data-color="#FFDD00" data-emoji="🍺"  data-font="Cookie" data-text="Buy me a beer" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
"""

html(button, height=70, width=220)

st.markdown(
    """
    <style>
        iframe[width="220"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("💸 Portfolio Rebalancing App 💸")
st.markdown('### Instructions')
st.write("Enter your current positions and desired allocations of your positions and cash in the table below. Then click the Rebalance button to calculate the proposed action plan. At this time, only a single consistent currency is support. Do not mix currencies.")
st.write('Tips:')
st.write("- The ticker column should be ticker shown on [Yahoo Finance](https://ca.finance.yahoo.com/quote/BMO.TO/). For example, the ticker for BMO is BMO.TO.")
st.write('- The desired allocation column should be a number between 0 and 100. For example, 50.0 means 50% of your portfolio should be in that position. The sum of all desired allocations should be 100.0.')
st.write('- If you are on mobile, double tap the table to edit the cells.')




#gd.configure_column(field = '🔧',  
#                    onCellClicked = js_add_row,
#                    cellRenderer = cellRenderer_addButton,
#                    lockPosition='left')
#gd.configure_column(field = '🗑',
#                    onCellClicked = js_delete_row,
#                    cellRenderer = cellRenderer_deleteButton,
#                    lockPosition='left')


# This part for updating the Grid so that Streamlit doesnot rerun from whole
cols = st.columns(2)
with cols[0]:
    n = st.number_input("Number of Tickers", value = 3, min_value = 1, max_value = 10, step = 1)
with cols[1]:
    transaction_fee = st.number_input("Flat Trading Fee ($) (per trade)", value = 6.95, min_value = 0.0, max_value = 100.0, step = 0.1)
with st.form('Positions') as f:

    st.header('Positions Inputs 🔖 (edit me like an Excel sheet)!')
    df = pd.DataFrame({
    'Ticker': ['cash', 'XAW.TO', 'ZAG.TO', 'VCN.TO'] + ['Placeholder'] * (n - 3),
    'Shares': [6500] + [100, 400, 300] + [0] * (n - 3),
    'Desired Allocation (%)': [1, 33, 33, 33] + [0] * (n - 3),
    })
    numeric_df = df[['Shares', 'Desired Allocation (%)']]
    numeric_df= numeric_df.applymap(lambda x: pd.to_numeric(x, errors='coerce'))

    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_default_column(editable=True)
    gd.configure_column(field = 'Desired Allocation (%)', width = 400)
    #gd.configure_column(field = 'Price ($)', width = 160)
    gd.configure_column(field = 'Ticker', width = 150)
    gridoptions = gd.build()
    ag_grid  = AgGrid(df,
                    gridOptions = gridoptions, 
                    editable=True,
                    allow_unsafe_jscode = True,
                    theme = 'balham',
                    height = 200,
                    fit_columns_on_grid_load = True)

    if st.form_submit_button("Rebalance", type="primary"):
        df = ag_grid['data']
        df = df[~((df['Shares'] == 0) & (df['Desired Allocation (%)'] == 0))]
        df['Price ($)'] = df['Ticker'].apply(lambda x: get_price_vantage(x))
        if df['Desired Allocation (%)'].sum() != 100:
            st.error('Desired Allocation must sum to 100%')
            st.stop()
        prices = df['Price ($)'].values
        names = df['Ticker'].values
        quantities = df['Shares'].values
        allocations = df['Desired Allocation (%)'].values
        fee = transaction_fee * df[df.Ticker != 'cash'].shape[0]

        new_quantities = calculate_rebalanced_portfolio(prices, quantities, allocations, fee)
        total_value = sum(float(prices[i]) * float(quantities[i]) for i in range(len(prices)))
        st.write(f'Your portfolio value is ${total_value:,.2f}.')
        st.write(f'Your total trading fees will be ${fee:,.2f}.')
        df = update_table(df, new_quantities, transaction_fee)
        cash = df[df['Ticker'] == 'cash']['Dollar Value'].values[0]
        df['price'] = df['Price ($)']
        port_value_new = df["Desired Dollar Value"].sum() - fee

        for c in ['Price ($)', 'Dollar Value', 'Desired Dollar Value']:
            df[c] = df[c].apply(lambda x: "${:,.2f}".format(x))
        for c in ['Desired Allocation (%)', 'Current Allocation (%)', 'Desired Shares', 'Shares']:
            df[c] = df[c].apply(lambda x: "{:,.2f}".format(x))

        st.write('Calculations table:')
        st.write(df[[x for x in df.columns if x != 'price']])
        df = df.sort_values('price', ascending=False)
        #st.write(df)

        def get_action_plan(df, allow_fractional_shares = True):
            prices = df['Price ($)'].values
            names = df['Ticker'].values
            new_quantities = [float(x.replace(',','')) for x in df['Desired Shares'].values]
            quantities = [float(x.replace(',','')) for x in df['Shares'].values]
            action_plan = []
            sell_actions = []
            buy_actions = []
            for i in range(len(prices)):
                if names[i] != 'cash':
                    if new_quantities[i] > quantities[i]:
                        a = new_quantities[i] - quantities[i]
                        if allow_fractional_shares:
                            action = f"Buy {a:.2f} shares of {names[i]}"
                        else:
                            action = f"Buy {math.floor(a)} shares of {names[i]}"
                        buy_actions.append(action)
                    elif new_quantities[i] < quantities[i]:
                        a = quantities[i] - new_quantities[i]
                        if allow_fractional_shares:
                            action = f"Sell {a:.2f} shares of {names[i]}"
                        else:
                            action = f"Sell {math.ceil(a)} shares of {names[i]}"
                        sell_actions.append(action)
                    else:
                        action = f"No action needed for {names[i]}"
                        sell_actions.append(action)

            action_plan = sell_actions + buy_actions
            return action_plan
        action_plan = get_action_plan(df)
        st.write('💡 Pro tip: Sell first, then buy.')
        st.markdown("### 📝 Action plan (fractional shares):")
        for action in action_plan:
            st.write("- " + action)
        st.write('Your portfolio value after trading and fees will be ${:,.2f}'.format(port_value_new))

        st.write('💡 Pro tip: If your trading platform does not support fractional shares, take the following conservative action plan:')
        action_plan = get_action_plan(df, False)
        st.markdown("### 📝 Action plan (no fractional shares):")
        for action in action_plan:
            st.write("- " + action)
        st.balloons()



show_disclaimer = st.button("Disclaimer")
if show_disclaimer or st.session_state.get('show_disclaimer'):
    st.session_state['show_disclaimer'] = True
    st.markdown(legal_disclaimer(), unsafe_allow_html=True)
else:
    st.write("")

