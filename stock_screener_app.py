import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Stock Screener & Visualizer", layout="wide")

st.title("Stock Screener & Visualizer")
st.markdown("Filter NSE stocks based on key financial ratios and view their price trends.")

stock_symbols = {
    'Reliance': 'RELIANCE.NS',
    'Infosys': 'INFY.NS',
    'HDFC Bank': 'HDFCBANK.NS',
    'TCS': 'TCS.NS',
    'ICICI Bank': 'ICICIBANK.NS',
    'Kotak Bank': 'KOTAKBANK.NS',
    'Bharti Airtel': 'BHARTIARTL.NS',
    'Adani Ports': 'ADANIPORTS.NS',
    'SBI': 'SBIN.NS',
    'Wipro': 'WIPRO.NS'
}

selected_stocks = st.multiselect("Select Stocks to Analyze", list(stock_symbols.keys()), default=["Reliance"])


st.sidebar.header("Filter Criteria")
pe_range = st.sidebar.slider("P/E Ratio", 0.0, 100.0, (0.0, 50.0))
pb_range = st.sidebar.slider("P/B Ratio", 0.0, 20.0, (0.0, 10.0))
div_yield_min = st.sidebar.slider("Min Dividend Yield (%)", 0.0, 10.0, 0.0)
roe_min = st.sidebar.slider("Min ROE (%)", 0.0, 50.0, 0.0)

filtered_data = []

st.subheader("Filtered Stock Table")

for name in selected_stocks:
    symbol = stock_symbols[name]
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        pe = info.get("trailingPE", None)
        pb = info.get("priceToBook", None)
        roe = info.get("returnOnEquity", None)
        dy = info.get("dividendYield", None)

        if roe is not None:
            roe *= 100
        if dy is not None:
            dy *= 100

        if (pe is not None and pb is not None and roe is not None and dy is not None and
            pe_range[0] <= pe <= pe_range[1] and
            pb_range[0] <= pb <= pb_range[1] and
            dy >= div_yield_min and
            roe >= roe_min):
            
            filtered_data.append({
                "Stock": name,
                "P/E": round(pe, 2),
                "P/B": round(pb, 2),
                "ROE (%)": round(roe, 2),
                "Dividend Yield (%)": round(dy, 2),
            })
    except Exception as e:
        st.warning(f"Could not load data for {name}: {e}")

df = pd.DataFrame(filtered_data)

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks matched your filters.")


st.subheader("Stock Price Charts")

for name in selected_stocks:
    symbol = stock_symbols[name]
    try:
        data = yf.download(symbol, period="6mo", progress=False)
        fig = px.line(data, x=data.index, y='Adj Close', title=f'{name} Price (Last 6 Months)')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching chart for {name}: {e}")
