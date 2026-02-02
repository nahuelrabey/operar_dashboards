# Proposal: Candle Return Analysis (Earning/Loss)

## Goal
Allow users to visualize the **Per-Candle Earning/Loss** (Intraday Return) instead of the **Cumulative Return**. This helps in analyzing the specific performance of each interval (e.g., each day's trading session) accurately, without the compounding effect or overnight gaps.

## Proposed Changes

### 1. UI Updates (`pages/01_CEDEARs_Analysis.py`)
- Add a **"Graph Metric"** selector inside the graph configuration form (or above it):
    - Options:
        - `Cumulative Return (%)` (Current default)
        - `Candle Return (%)` (New)
- Updates the methodology explanation to include the new metric.

### 2. Logic Updates (`src/analysis.py`)
- **Calculation Logic**:
    - **Candle Return**: Represents the percentage move within the candle's duration (Open to Close).
    - Formula: $$\\frac{Close - Open}{Open} \\times 100$$
    - This effectively isolates the trading session performance, ignoring overnight gaps (Open vs previous Close).

### 3. Visualization
- **Line Chart**: The standard Line Chart will be used.
- **Interpretation**: 
    - A value of `+1.5` means the asset gained 1.5% from its Open to its Close during that specific interval.
    - This series will likely oscillate around 0, showing volatility and daily strength/weakness.

## Implementation Details
- Add `calculate_candle_returns(df)` or update existing normalization logic to support this mode.
- In `src/analysis.py`, add `calculate_candle_pct_change(series_open, series_close)`.
