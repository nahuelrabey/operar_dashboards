# Proposal: Multi-Timeframe Correlation Analysis

## Goal
Expand the correlation analysis to include longer time horizons: **1 Month, 3 Months, 6 Months, and 12 Months**. This allows the user to judge the consistency of the correlation over time, distinguishing between short-term noise and long-term trends.

## Proposed Changes

### 1. UI Updates (`pages/01_CEDEARs_Analysis.py`)
- **Mode Selection**: Introduce a "Correlation Mode" in the sidebar or a generic "Analysis Mode".
    - **Current (Short Term)**: Existing functionality (Intraday/Daily for last week/month).
    - **Proposed (Long Term)**: A new view dedicated to the requested periods (1M, 3M, 6M, 1Y).
- **Long Term View**:
    - Instead of a single "Correlation" column, the table will display **multiple columns**:
        - `Ticker`
        - `1M` (Correlation over last 20 trading days)
        - `3M` (Last 60 days)
        - `6M` (Last 126 days)
        - `1Y` (Last 252 days)
    - **Graph Visualization**:
        - Selecting a ticker will plot the full **1 Year Daily Price History** (normalized) vs GLD.
        - This provides the visual context for the long-term metrics.

### 2. Logic Updates (`src/analysis.py`)
- **Data Fetching**:
    - Fetch **1 Year** of data with **1 Day** interval for all tickers.
    - Use `fetch_batch_candles(period="1y", interval="1d")`.
- **Calculation Logic**:
    - Create a new function `calculate_multi_period_correlations(df_prices, df_benchmark)`:
        - Input: 1Y Daily Data.
        - Process:
            - Slice data for the last 1M, 3M, 6M, 1Y.
            - Calculate correlation for each slice against GLD.
            - Combine results into a single DataFrame.
        - Output: DataFrame with columns [`Ticker`, `1M`, `3M`, `6M`, `1Y`].

### 3. Implementation Steps
1.  **Modify Sidebar**: Add a toggle or selector for "Analysis Type": `Intraday (Short Term)` vs `Historical (Long Term)`.
2.  **Logic Implementation**:
    - If `Historical` is selected:
        - Fetch 1y/1d data.
        - Compute multi-period correlations.
        - Display the Multi-Column Table (with `st.data_editor` for graph selection).
    - If `Intraday` is selected:
        - Keep existing behavior (Interval selector + single period correlation).

## Benefits
- **Efficiency**: One data fetch (1Y Daily) serves all 4 new metrics.
- **Clarity**: Side-by-side comparison of short vs long term correlation helps identify true proxies vs temporary alignments.
