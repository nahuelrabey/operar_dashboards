# Proposal: Graph Visualization in Correlation Table

## Goal
Enable users to visually compare the performance of specific CEDEARs against Gold (GLD) directly from the Correlation table. By checking a box next to a ticker, a line graph comparing its price evolution with GLD will be displayed.

## Proposed Changes

### 1. UI Updates (`pages/01_CEDEARs_Analysis.py`)
- Replace the static `st.dataframe` for the correlation table with `st.data_editor`.
- Add a new boolean column `"Show Graph"` to the correlation DataFrame, initialized to `False`.
- Configure this column as a `st.column_config.CheckboxColumn`.
- Below the table, display a line chart for *each* checked ticker (or a combined chart).

### 2. Logic Updates
- **Data Fetching for Plot**:
    - The `calculate_correlations` function currently returns only the correlation coefficient.
    - To plot, we need the historical price series.
    - Since we have implemented caching, we can simply re-call `market_data.fetch_candles` (or batch) for the *checked* tickers using the same `period` and `interval` as the analysis. This will hit the cache and be fast.
- **Normalization**:
    - Since GLD (approx $200+) and CEDEARs (varied ARS prices) have different scales, plotting raw prices on one chart is unreadable.
    - **Approach**: Normalize prices to percentage change (Cumulative Return) starting at 0% for the period. 
    - Formula: `(Price_t / Price_0 - 1) * 100`.

### 3. Implementation Steps
1.  Update `pages/01_CEDEARs_Analysis.py`:
    - Capture the edited DataFrame from `st.data_editor`.
    - Filter rows where `"Show Graph"` is True.
    - If any selected:
        - Fetch GLD series (cached).
        - Loop through selected tickers:
            - Fetch Ticker series (cached).
            - Normalize both and align indices.
            - combine into a DataFrame.
        - Display `st.line_chart` with the combined data.

## Dependencies
- Streamlit (`st.data_editor`, `st.line_chart`).
- Pandas (normalization logic).
- Existing `src.market_data` (caching ensures performance).

## New Functions (Internal Helper)
*No public API changes to `src/analysis.py` strictly required, but a helper in the page or analysis module is useful.*

- `normalize_to_pct_change(series: pd.Series) -> pd.Series`:
    - Input: Price Series.
    - Output: Percentage change series starting at 0 (Cumulative Return) to allow comparison.
