import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import plotly.graph_objects as go
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

# Analysis Type Selection
analysis_type = st.sidebar.radio("Analysis Type", ["Short Term (Intraday)", "Historical (Long Term)"])

if analysis_type == "Short Term (Intraday)":
    # Interval Selection
    interval_options = {
        "Daily": "1d",
        "Hourly": "1h",
        "30 Minutes": "30m",
        "15 Minutes": "15m",
        "5 Minutes": "5m"
    }
    selected_interval_label = st.sidebar.selectbox("Select Analysis Interval", list(interval_options.keys()), index=1)
    selected_interval = interval_options[selected_interval_label]

    # Map interval to suitable period (Yahoo limits)
    # <60m data is limited to 60 days.
    if selected_interval == "1d":
        analysis_period = "1mo"
    else:
        analysis_period = "5d" # 5 days for intraday to keep it fast and relevant
else:
    # Historical Defaults
    selected_interval = "1d"
    analysis_period = "1y"

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Configuration Guide**:\n"
    "- **Select Date**: Choose the date to view daily performance (Gainers/Losers). If the date is a holiday/weekend, the latest available data is shown.\n"
    "- **Refresh Data**: Clears the local cache and forces a fresh download of market data from Yahoo Finance.\n"
    "- **Refresh Data**: Clears the local cache and forces a fresh download of market data from Yahoo Finance.\n"
    "- **Analysis Type**: Switch between Short Term (Intraday/Daily) and Long Term (Historical) views."
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
st.divider()
if analysis_type == "Short Term (Intraday)":
    st.header(f"Correlation with Gold (GLD) - {selected_interval_label}")
else:
    st.header("Correlation with Gold (GLD) - Historical (1 Year)")

with st.expander("ℹ️ Methodology Explanation"):
    st.markdown("""
    **1. Correlation Calculation**:
    - Represents the **Pearson correlation coefficient** calculated using the **Close Prices** of the ticker and the benchmark (GLD).
    - **Range**: -1 (Perfect Inverse) to +1 (Perfect Direct).
    - **Short Term**: Calculated using the selected interval data (e.g., 5-minute bars for the last 5 days).
    - **Historical**: Calculated using Daily Close prices over the specific window (1 Month, 3 Months, etc.).

    **2. Performance Comparison Graph**:
    - **Cumulative Return (%)**:
        - Shows the percentage growth over time.
        - *Long Term*: Uses Open price of start day as baseline.
        - *Short Term*: Uses first Close price as baseline.
        - Formula: $$\\frac{Price_t - Baseline}{Baseline} \\times 100$$
    - **Candle Return (%)**:
        - Shows the percentage change *within* each specific interval (Close vs Open).
        - Isolates each session's performance, ignoring overnight gaps.
        - Formula: $$\\frac{Close_t - Open_t}{Open_t} \\times 100$$
    """)

try:
    with st.spinner(f"Fetching {selected_interval} data for correlation..."):
        # We need the list of tickers again.
        if tickers_list:
             if analysis_type == "Short Term (Intraday)":
                corr_df = analysis.calculate_correlations(tickers_list, benchmark_ticker="GLD", period=analysis_period, interval=selected_interval)
             else:
                corr_df = analysis.calculate_multi_period_correlations(tickers_list, benchmark_ticker="GLD")
             
             if not corr_df.empty:
                # Add "Show Graph" column (default False)
                corr_df["Show Graph"] = False
                
                # Make "Show Graph" the first column
                cols = ["Show Graph"] + [c for c in corr_df.columns if c != "Show Graph"]
                corr_df = corr_df[cols]

                # Form for batching updates
                with st.form("correlation_graph_form"):
                    # Graph Config
                    graph_metric = st.radio("Graph Metric", ["Cumulative Return (%)", "Candle Return (%)"], horizontal=True)

                    # Display interactive editor
                    edited_df = st.data_editor(
                        corr_df,
                        column_config={
                            "Show Graph": st.column_config.CheckboxColumn(
                                "Graph",
                                help="Select to view performance comparison graph",
                                default=False,
                            ),
                            "Correlation": st.column_config.NumberColumn(
                                format="%.4f"
                            )
                        },
                        disabled=["Ticker", "Correlation", "1M", "3M", "6M", "1Y"],
                        hide_index=True,
                        width="stretch"
                    )
                    
                    update_graph = st.form_submit_button("Update Graph")
                
                # Plotting Logic
                if update_graph:
                    selected_tickers = edited_df[edited_df["Show Graph"]]["Ticker"].tolist()
                    
                    if selected_tickers:
                        st.subheader("Performance Comparison (vs GLD)")
                        
                        with st.spinner("Preparing graph..."):
                            
                            # Helper to process data based on metric
                            def get_series_data(df, metric, analysis_type_param):
                                if df.empty: return None
                                
                                closes = analysis._get_close_data(df)
                                if isinstance(closes, pd.DataFrame): closes = closes.iloc[:,0]
                                
                                if metric == "Candle Return (%)":
                                    opens = analysis._get_open_data(df)
                                    if isinstance(opens, pd.DataFrame): opens = opens.iloc[:,0]
                                    return analysis.calculate_candle_return(opens, closes)
                                else:
                                    # Cumulative Return
                                    baseline = None
                                    if analysis_type_param == "Historical (Long Term)":
                                        opens = analysis._get_open_data(df)
                                        if isinstance(opens, pd.DataFrame): opens = opens.iloc[:,0]
                                        if not opens.empty:
                                            baseline = opens.iloc[0]
                                    
                                    return analysis.normalize_to_pct_change(closes, baseline=baseline)

                            # Fetch GLD (Benchmark)
                            df_gold_bench = analysis.market_data.fetch_candles("GLD", period=analysis_period, interval=selected_interval)
                            comparison_data = pd.DataFrame()
                            
                            s_gld = get_series_data(df_gold_bench, graph_metric, analysis_type)
                            if s_gld is not None:
                                comparison_data["GLD"] = s_gld
                            
                            # Fetch and Normalize Selected Tickers
                            for ticker in selected_tickers:
                                df_t = analysis.market_data.fetch_candles(ticker, period=analysis_period, interval=selected_interval, suffix="")
                                s_t = get_series_data(df_t, graph_metric, analysis_type)
                                if s_t is not None:
                                    comparison_data[ticker] = s_t
                            
                            if not comparison_data.empty:
                                # Remove rows with NaN (gaps where data is missing in any series)
                                comparison_data.dropna(inplace=True)
                                
                                # Plotly uses native Datetime objects, so no string conversion needed.

                                # st.line_chart(comparison_data, height=600)
                                # Plotly Logic
                                fig = go.Figure()
                                
                                # Add traces
                                for col in comparison_data.columns:
                                    fig.add_trace(go.Scatter(
                                        x=comparison_data.index,
                                        y=comparison_data[col],
                                        mode='lines',
                                        name=col
                                    ))
                                
                                # Layout Configuration
                                fig.update_layout(
                                    title="Performance Comparison",
                                    xaxis_title="Date",
                                    yaxis_title=graph_metric,
                                    height=600,
                                    hovermode="x unified",
                                    xaxis=dict(
                                        type='date',
                                        rangeslider=dict(visible=True),
                                    )
                                )

                                # Gap Removal Logic (Weekends)
                                # Only apply if it's daily data or if we want to risk it with intraday.
                                # For simple weekend removal on daily data:
                                if "d" in selected_interval:
                                     # Remove Saturday/Sunday
                                     # Daterange bounds: Saturday (6) to Monday (1) excluded? 
                                     # Plotly rangebreaks: values=... or bounds=["sat", "mon"]
                                     fig.update_xaxes(
                                         rangebreaks=[
                                             dict(bounds=["sat", "mon"]), # hide weekends
                                         ]
                                     )
                                elif selected_interval in ["1h", "30m", "15m", "5m"]:
                                    # For intraday, hiding non-trading hours is tricky without complex patterns.
                                    # But hiding weekends is always safe.
                                     fig.update_xaxes(
                                         rangebreaks=[
                                             dict(bounds=["sat", "mon"]), # hide weekends
                                         ]
                                     )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("No data available for the selected tickers.")
             else:
                st.warning("No overlapping data found for Correlation.")
        else:
             st.warning("No tickers to calculate correlation.")

except Exception as e:
    st.error(f"Error processing correlation: {e}")
