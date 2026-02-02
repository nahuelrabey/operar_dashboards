# Proposal: Dynamic Interval Selection

## Goal
Allow users to select the time interval (granularity) for the market analysis, rather than using fixed defaults (currently `Daily` for performance and `Hourly` for correlation).

## Proposed Changes

### 1. UI Updates (`pages/01_CEDEARs_Analysis.py`)
Add a new selection box in the **Settings** sidebar.

```python
interval_options = {
    "Daily": "1d",
    "Hourly": "1h",
    "30 Minutes": "30m",
    "15 Minutes": "15m",
    "5 Minutes": "5m"
}
selected_interval_label = st.sidebar.selectbox("Select Interval", list(interval_options.keys()))
selected_interval = interval_options[selected_interval_label]
```

### 2. Logic Updates (`src/analysis.py` & `pages/...`)

The `period` (how far back to look) often depends on the `interval`.
- **1d**: Can fetch 1mo, 1y, etc.
- **1h**: Max 730 days (yfinance constraint).
- **Intraday (<1h)**: Max 60 days (yfinance constraint).

**Strategy:**
Auto-adjust the default `period` based on the selected `interval` to ensure valid data fetching, while allowing user override if needed (future feature).

| Interval | Proposed Period | Reason |
| :--- | :--- | :--- |
| `1d` | `1mo` | Sufficient for monthly trend and daily changes. |
| `1h` | `1mo` | Granular enough for recent weeks. |
| `30m` | `1mo` | Balanced. |
| `15m` | `1mo` | Balanced. |
| `5m` | `5d` | Very granular, keeps data size manageable and within Yahoo limits (60d). |

### 3. Implementation Steps
1.  Add `selectbox` to sidebar.
2.  Define a helper to map `interval` -> `default_period`.
3.  Pass the `selected_interval` and calculated `period` to:
    *   `load_market_data()` for the Daily Performance section.
    *   `calculate_correlations()` for the Correlation section.

### 4. Cache Implications
The existing file-based cache logic in `src/market_data.py` uses arguments hashing.
- Changing the interval will correctly generate **new cache files** (e.g., `fetch_candles_AAPL_...1h...` vs `...5m...`).
- No changes needed in the caching layer.
