from st_aggrid import JsCode
import requests
import streamlit as st
import dotenv 
import os
import yfinance as yf

dotenv.load_dotenv()
# JavaScript function for the delete button
js_delete_row = JsCode("""
function(e) {
    var api = e.api;
    var rowIndex = e.rowIndex;
    api.updateRowData({remove: [api.getDisplayedRowAtIndex(rowIndex).data]});
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


js_add_row = JsCode("""
function(e) {
    var api = e.api;
    var rowPos = e.rowIndex + 1; 
    var nextStock = String.fromCharCode(e.api.getDisplayedRowAtIndex(e.rowIndex).data.Stock.charCodeAt(e.api.getDisplayedRowAtIndex(e.rowIndex).data.Stock.length - 1) + 1);
    api.applyTransaction({addIndex: rowPos, add: [{Stock: "Stock " + nextStock, Price: 0, Quantity: 0, "Allocation (%)": 0}]})    
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
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        data = requests.get(f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}').json()
        price = data["Global Quote"]["05. price"]
    except KeyError:
        stock = yf.Ticker(symbol)
        price = stock.info['regularMarketPrice']
    except Exception:
        st.warning(f'Error getting price for {symbol}')
        price = None
    return float(price)

def get_price_yahoo(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.info['regularMarketPrice']
    except Exception:
        st.warning(f'Error getting price for {symbol}')
        price = 0
    return price