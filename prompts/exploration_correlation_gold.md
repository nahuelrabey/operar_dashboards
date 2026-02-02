# Proposal: CEDEARs Analysis Dashboard

## Goal
Create a Streamlit dashboard to visualize:
1.  **Daily Performance**: Top 5 Gainers and Losers for a specific date (e.g., 30/01/2026).
2.  **Market Correlation**: Correlation of all CEDEARs against Gold (using GLD as proxy) over the last week.

## Architecture

### 1. Data Source
- **Library**: `market_data.py` (already created).
- **Input**: `cedears.csv` for the list of tickers.
- **External Data**: `yfinance` for market data (CEDEARs + Gold/GLD).

### 2. Streamlit App Structure (`dashboard.py`)
- **Sidebar**:
    - Date picker (default 30/01/2026).
    - "Refresh Data" button.
- **Main Page**:
    - **Header**: Dashboard Title & Status.
    - **Section 1: Daily Movers**
        - Two columns: "Top Gainers" and "Top Losers".
        - Metrics: Ticker, Price, Change %.
    - **Section 2: Gold Correlation**
        - Table showing CEDEAR tickers and their correlation coefficient with GLD.
        - Option to filter/sort by correlation strength.

### 3. Implementation Details
- **Data Fetching**:
    - Since fetching 200+ tickers individually via `yfinance` is slow, we will use `yf.download(tickers, ...)` in batches or all at once (multithreaded by yfinance).
    - We will cache the data using `@st.cache_data` to avoid re-fetching on every interaction.
- **Calculations**:
    - **Daily Change**: $(Close_{today} - Close_{yesterday}) / Close_{yesterday}$.
    - **Correlation**:
        - Fetch close prices for all CEDEARs + GLD (or GC=F) for `period="1wk", interval="1h"`.
        - Create a single DataFrame with all closes.
        - Compute `.corrwith()` against the Gold column.

### 4. Dependencies
- `streamlit`
- `pandas`
- `yfinance`
- `matplotlib` / `plotly` (optional, for charts if needed later).

## Next Steps
1.  Install `streamlit`.
2.  Create `dashboard.py`.
3.  Implement data fetching with caching.
4.  Build the UI components.