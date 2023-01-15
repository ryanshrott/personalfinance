import streamlit as st

def rebalance_portfolio(stock_a_alloc, stock_b_alloc, cash_alloc, stock_a_price, stock_b_price,
                       stock_a_qty, stock_b_qty, cash_qty):
    # Calculate the total value of the portfolio
    total_value = stock_a_qty * stock_a_price + stock_b_qty * stock_b_price + cash_qty

    # Calculate the target allocation for each asset
    stock_a_target_alloc = total_value * stock_a_alloc
    stock_b_target_alloc = total_value * stock_b_alloc
    cash_target_alloc = total_value * cash_alloc

    # Calculate the difference between the target and current allocations for each asset
    stock_a_diff = stock_a_target_alloc - (stock_a_qty * stock_a_price)
    stock_b_diff = stock_b_target_alloc - (stock_b_qty * stock_b_price)
    cash_diff = cash_target_alloc - cash_qty

    # Display the action plan for rebalancing the portfolio
    st.write("To rebalance your portfolio, follow these steps:")
    if stock_a_diff > 0:
        st.write(f" - Buy {stock_a_diff / stock_a_price:.2f} shares of Stock A")
    elif stock_a_diff < 0:
        st.write(f" - Sell {abs(stock_a_diff / stock_a_price):.2f} shares of Stock A")
    if stock_b_diff > 0:
        st.write(f" - Buy {stock_b_diff / stock_b_price:.2f} shares of Stock B")
    elif stock_b_diff < 0:
        st.write(f" - Sell {abs(stock_b_diff / stock_b_price):.2f} shares of Stock B")
    if cash_diff > 0:
        st.write(f" - Use {cash_diff:.2f} cash to buy more assets")
    elif cash_diff < 0:
        st.write(f" - Sell assets to generate {abs(cash_diff):.2f} cash")


def main():
    st.title("Portfolio Rebalancer")

    stock_a_alloc = st.sidebar.slider("Allocation for Stock A", 0.0, 1.0, 0.8)
    stock_b_alloc = st.sidebar.slider("Allocation for Stock B", 0.0, 1.0, 0.2)
    cash_alloc = 1.0 - stock_a_alloc - stock_b_alloc
    st.sidebar.markdown(f"Allocation for cash: {cash_alloc:.2f}")

    stock_a_price = st.number_input("Current price of Stock A", value=100.0)
    stock_b_price = st.number_input("Current price of Stock B", value=100.0)
    stock_a_qty = st.number_input("Quantity of Stock A", value=10)
    stock_b_qty = st.number_input("Quantity of Stock B", value=10)
    cash_qty = st.number_input("Current cash position", value=1000.0)

    if st.button("Rebalance Portfolio"):
        rebalance_portfolio(stock_a_alloc, stock_b_alloc, cash_alloc, stock_a_price, stock_b_price,
                            stock_a_qty, stock_b_qty, cash_qty)

if __name__ == "__main__":
    main()

