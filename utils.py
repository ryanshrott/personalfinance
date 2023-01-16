from st_aggrid import JsCode
import requests
import streamlit as st
import dotenv 
import os
import yfinance as yf

dotenv.load_dotenv()


def update_table(data, new_quantities, transaction_fee = 0.0):
    price = data['Price ($)']
    quantity = data.Shares
    total_value = sum(price[i] * quantity[i] for i in range(len(price)))
    current_allocation = (price * quantity)/total_value*100
    data["Current Allocation (%)"] = current_allocation
    data['Dollar Value'] = price * quantity
    data['Desired Shares'] = new_quantities
    data['Trading Fee'] = data['Ticker'].apply(lambda x: transaction_fee if x != 'cash' else 0)
    data['Desired Dollar Value'] = data['Desired Shares'] * data['Price ($)']
    return data[['Ticker', 'Price ($)', 'Shares',  'Desired Shares', 'Dollar Value', 'Desired Dollar Value', 'Current Allocation (%)', 'Desired Allocation (%)', 'Trading Fee']]

def calculate_rebalanced_portfolio(prices, quantities, allocations, fee):
    total_value = sum(prices[i] * quantities[i] for i in range(len(prices))) - fee
    new_quantities = [0] * len(prices)
    for i in range(len(prices)):
        new_quantities[i] = (allocations[i]/100.0* total_value) / prices[i]
    return new_quantities


js_add_row = JsCode("""
function(e) {
    let api = e.api;
    let rowPos = e.rowIndex + 1; 
    api.applyTransaction({addIndex: rowPos, add: [{}]})    
};
"""     
)  

js_delete_row = JsCode("""
function(e) {
let api = e.api;
let selectedRow = api.getFocusedCell();
let node = api.getRowNode(selectedRow.rowIndex);
api.applyTransaction({ remove: [node.data] })
};
""")

# cellRenderer for the delete button
cellRenderer_deleteButton = JsCode('''
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <style>
                .btn_delete {
                    background-color: #f44336;
                    border: 2px solid black;
                    color: white;
                    text-align: center;
                    display: inline-block;
                    font-size: 12px;
                    font-weight: bold;
                    height: 2em;
                    width: 10em;
                    border-radius: 12px;
                    padding: 0px;
                }
                </style>
                <button id='click-button' 
                    class="btn_delete" 
                    >&#x2718; Delete</button>
            </span>
        `;
        }
        getGui() {
            return this.eGui;
        }
    };
    ''')


# cellRenderer for the delete button
cellRenderer_deleteButton = JsCode('''
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <style>
                .btn_delete {
                    background-color: #f44336;
                    border: 2px solid black;
                    color: white;
                    text-align: center;
                    display: inline-block;
                    font-size: 12px;
                    font-weight: bold;
                    height: 2em;
                    width: 10em;
                    border-radius: 12px;
                    padding: 0px;
                }
                </style>
                <button id='click-button' 
                    class="btn_delete" 
                    >&#x2718; Delete</button>
            </span>
        `;
        }
        getGui() {
            return this.eGui;
        }
    };
    ''')


# JavaScript function 
# api.applyTransaction({add: [{}]})   # This line would end row at the end always 
# Finding row index is important to add row just after the selected index
js_add_row = JsCode("""
function(e) {
    let api = e.api;
    let rowPos = e.rowIndex + 1; 
    api.applyTransaction({addIndex: rowPos, add: [{}]})    
};
"""     
)  

# cellRenderer with a button component.
# Resources:
# https://blog.ag-grid.com/cell-renderers-in-ag-grid-every-different-flavour/
# https://www.w3schools.com/css/css3_buttons.asp
cellRenderer_addButton = JsCode('''
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <style>
                .btn_add {
                    background-color: #71DC87;
                    border: 2px solid black;
                    color: #D05732;
                    text-align: center;
                    display: inline-block;
                    font-size: 12px;
                    font-weight: bold;
                    height: 2em;
                    width: 10em;
                    border-radius: 12px;
                    padding: 0px;
                }
                </style>
                <button id='click-button' 
                    class="btn_add" 
                    >&#x2193; Add</button>
            </span>
        `;
        }
        getGui() {
            return this.eGui;
        }
    };
    ''')

def get_price_vantage(symbol):
    if symbol == 'CASH' or symbol=='cash' or symbol=='Cash':
        return 1
    if 'Ticker' in symbol:
        return 0.0000001
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        data = requests.get(f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}').json()
        price = data["Global Quote"]["05. price"]
    except KeyError:
        try:
            Ticker = yf.Ticker(symbol)
            price = Ticker.info['regularMarketPrice']
        except Exception:
            st.error(f'Error getting price for {symbol}')
            price = None
    return float(price)

def get_price_yahoo(symbol):
    try:
        Ticker = yf.Ticker(symbol)
        price = Ticker.info['regularMarketPrice']
    except Exception:
        st.warning(f'Error getting price for {symbol}')
        price = 0
    return price

def legal_disclaimer():
    disclaimer = """
    <div style="font-size:9px;">
    The information provided by this webapp is for general informational purposes only and is not intended to be a substitute for professional financial advice. The webapp is not responsible for any losses incurred as a result of using the information provided on the website. Users are solely responsible for ensuring that the information provided by the webapp is accurate and suitable for their individual needs. While we strive to provide accurate and up-to-date information, we cannot guarantee that all prices reflected on the webapp are 100% accurate and reflect current market conditions. The user acknowledges that the information provided on this webapp is subject to change without notice. By using this webapp, the user agrees to the terms of this disclaimer and releases the webapp and its owners from any and all liability.
    </div>
    """
    return disclaimer