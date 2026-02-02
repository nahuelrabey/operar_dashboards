# Proposal: Market Data Caching Strategy

## Context
The application relies on `yfinance` to fetch historical market data. Repeatedly fetching the same data (e.g., during development or when navigating between pages) is inefficient, slow, and risks hitting API rate limits.

## Goal
Implement a simple, persistent caching mechanism to store fetched market data locally, reducing network calls and improving application responsiveness.

## Proposed Solution: File-Based Pickle Cache

We will implement a decorator-style or explicit wrapper around the `yfinance` calls in `src/market_data.py`.

### Storage
- **Location**: `data/cache/`
- **Format**: Python `pickle` (`.pkl`) files.
    - *Reasoning*: Pickle is the native serialization format for Pandas DataFrames, preserving indices, dtypes, and metadata perfectly without the overhead/precision loss of CSV.

### Naming Convention
To ensure unique cache keys for different requests, filenames will be generated using:
1.  **Function Name**: e.g., `fetch_candles`.
2.  **Readable Prefix**: e.g., `_AAPL` (to make manual inspection easier).
3.  **Arguments Hash**: An MD5 hash of the function arguments (tickers, period, interval, suffix).

**Format**: `{func_name}{readable_prefix}_{hash}.pkl`

### Invalidation Strategy
- **Manual/Explicit**: The user can modify the "Refresh Data" setting or click a button in the UI.
    - The "Refresh Data" button in the dashboard will clear the standard Streamlit cache (`st.cache_data.clear()`).
    - *Note*: Our custom file cache is persistent. To fully refresh, we might need to physically delete files or ignore them.
    - *Current Implementation*: The `load_market_data` function in the app handles the "Refresh" by re-calling the fetch functions. To force a re-fetch at the *library* level, we would typically delete the cache folder or add a `force_update` flag. For now, the implementation focuses on simple persistence: if the file exists, use it.

## Implementation Details

The `src/market_data.py` module will be updated to:
1.  Check `data/cache` for a matching file before calling `yfinance`.
2.  If found, load and return the DataFrame.
3.  If not found, fetch from API, save to `data/cache`, and return.

### Benefits
- **Offline/Bad Connection Capability**: Can work with previously fetched data.
- **Speed**: Loading a pickle file is orders of magnitude faster than a network request.
- **Simplicity**: No external database required (Redis, SQLite, etc.).
