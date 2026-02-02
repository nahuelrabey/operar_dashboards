# Project Structure Proposal

To support multiple dashboards and a growing codebase, I recommend adopting a standard Streamlit Multipage App structure combined with a `src` package for your business logic.

## Proposed Directory Tree

```text
operar_analysis/
├── app.py                   # Main entry point (Landing page)
├── pages/                   # Streamlit Pages (Auto-detected)
│   ├── 01_📊_CEDEARs_Analysis.py   # (The current dashboard.py)
│   └── 02_📈_Another_Dashboard.py  # Future dashboard
├── src/                     # Shared Library Code
│   ├── __init__.py
│   ├── market_data.py       # (Moved from root)
│   ├── extractors.py        # (Logic from extract_cedears.py)
│   ├── analysis.py          # [NEW] Analysis & Computation Logic (moved from dashboard.py)
│   └── utils.py             # Shared helpers
├── data/                    # Data Storage
│   ├── raw/                 # PDFs, etc.
│   └── processed/           # CSVs (cedears.csv)
├── prompts/                 # Documentation & Prompts
├── pyproject.toml           # Dependencies
└── README.md
```

## detailed Changes

1.  **`src/` Directory**:
    *   Move `market_data.py` here.
    *   Refactor `extract_cedears.py` into a reusable module (e.g., `src/extractors.py`) so dashboards can trigger extractions if needed, or keep it as a standalone script using `src` imports.

2.  **`pages/` Directory**:
    *   Streamlit automatically creates navigation for scripts in this folder.
    *   We will move the current `dashboard.py` logic into `pages/01_CEDEARs_Analysis.py`.
    *   **Crucially**, the data fetching, daily performance calculation, and correlation logic (currently mixed in the view) should be extracted to `src/analysis.py`. The dashboard should only handle UI rendering.
    *   **Proposed Functions for `src/analysis.py`**:
        *   `get_daily_performance(df_prices: pd.DataFrame, target_date: date) -> pd.DataFrame`:
            *   Input: The global dataframe of prices and the selected date.
            *   Logic: specific handling of "missing today", finding the previous available trading day, calculating % change, and returning a clean DataFrame of results (Ticker, Close, Change %).
        *   `calculate_correlations(tickers: list, benchmark: str = "GLD", period: str = "5d") -> pd.DataFrame`:
            *   Input: List of CEDEAR tickers.
            *   Logic: Fetches 1h data for both CEDEARs and the benchmark (in parallel/batch), performs the `lsuffix` join to avoid collisions (fixing the bug we just saw), and returns the sorted correlation series.

3.  **`data/` Directory**:
    *   Centralize `cedears.pdf` and `cedears.csv` here to keep the root clean.

4.  **`app.py`**:
    *   A simple "Home" page that introduces the project or shows high-level metrics.

## Implementation Steps
1.  Create folders: `src`, `pages`, `data`.
2.  Move `market_data.py` to `src/`.
3.  Move `cedears.csv` and `cedears.pdf` to `data/`.
4.  Refactor `dashboard.py` -> `pages/01_CEDEARs_Analysis.py` (updating imports and file paths).
5.  Create `app.py`.