import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
from src import market_data, analysis
import os

# Page config
st.set_page_config(page_title="CEDEARs Analysis", layout="wide")

st.title("CEDEARs Market Analysis")

# --- Sidebar ---
st.sidebar.header("Settings")
today = datetime.date.today()
default_date = today # Default to today
selected_date = st.sidebar.date_input("Select Date for Performance", default_date)
refresh_btn = st.sidebar.button("Refresh Data")

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Configuration Guide**:\n"
    "- **Select Date**: Choose the date to view daily performance (Gainers/Losers). If the date is a holiday/weekend, the latest available data is shown.\n"
    "- **Refresh Data**: Clears the local cache and forces a fresh download of market data from Yahoo Finance."
)

# --- Data Loading ---
@st.cache_data(ttl=3600, show_spinner="Fetching market data...")
def load_market_data():
    # 1. Load CEDEARs list
    csv_path = "data/cedears.csv"
    if not os.path.exists(csv_path):
        st.error(f"{csv_path} not found. Please run extract_cedears.py first.")
        return None, None
        
    try:
        df_cedears = pd.read_csv(csv_path)
        tickers = df_cedears['byma_code'].dropna().unique().tolist()
    except Exception as e:
        st.error(f"Error reading CEDEARs: {e}")
        return None, None

    # 2. Fetch Data for CEDEARs
    # Fetch CEDEARs
    df_cedears_data = market_data.fetch_batch_candles(tickers, period="1mo", interval="1d")
    
    return df_cedears_data, tickers

data_state = st.text("Loading data...")
df_prices, tickers_list = load_market_data()

if refresh_btn:
    st.cache_data.clear()
    df_prices, tickers_list = load_market_data()
data_state.empty()

if df_prices is None or df_prices.empty:
    st.warning("No data available.")
    st.stop()

# --- Daily Performance Section ---
st.header(f"Daily Performance")

df_performance = analysis.get_daily_performance(df_prices, selected_date)

if not df_performance.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 5 Gainers 🚀")
        st.dataframe(
            df_performance.sort_values("Change %", ascending=False).head(5)
            .style.format({"Close": "{:.2f}", "Prev Close": "{:.2f}", "Change %": "{:+.2f}%"})
        )
        
    with col2:
        st.subheader("Top 5 Losers 🔻")
        st.dataframe(
            df_performance.sort_values("Change %", ascending=True).head(5)
            .style.format({"Close": "{:.2f}", "Prev Close": "{:.2f}", "Change %": "{:+.2f}%"})
        )
else:
     st.info("No valid price changes found or insufficient data.")


# --- Correlation Section ---
st.divider()
st.header("Correlation with Gold (GLD) - Last Week")

try:
    with st.spinner("Fetching 1h data for correlation..."):
        # We need the list of tickers again.
        if tickers_list:
             corr_df = analysis.calculate_correlations(tickers_list, benchmark_ticker="GLD", period="5d")
             
             if not corr_df.empty:
                st.dataframe(
                    corr_df.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1).format({"Correlation": "{:.4f}"}),
                    use_container_width=True
                )
             else:
                st.warning("No overlapping data found for Correlation.")
        else:
             st.warning("No tickers to calculate correlation.")

except Exception as e:
    st.error(f"Error processing correlation: {e}")
