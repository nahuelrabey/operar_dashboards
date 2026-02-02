# Proposal: Correlation Lag

## Goal
Allow users to configure a **Lag** (shift) for the correlation calculation. This helps in identifying if a move in the Benchmark (GLD) at time $T$ consistently precedes a move in the Ticker at time $T+L$.

## Proposed Changes

### 1. UI Updates (`pages/01_CEDEARs_Analysis.py`)
- Add a **"Lag (Periods)"** number input in the correlation settings.
    - Default: `0`.
    - Min: `-10`, Max: `10` (or similar range).
    - Tooltip explains: "A positive lag checks if GLD(t) correlates with Ticker(t+Lag). Essentially, does GLD predict Ticker?"

### 2. Logic Updates (`src/analysis.py`)
- Update `calculate_correlations` and `calculate_multi_period_correlations` to accept `lag: int = 0`.
- **Shift Logic**:
    - We want correlation between `Benchmark` and `Ticker` where `Ticker` is shifted?
    - User Request: "If prices drops at day T, I wan't to know if there will be a drop/rise at that T+L".
    - So we compare `Benchmark(T)` with `Ticker(T+L)`.
    - In Pandas: `Ticker.shift(-L)` aligns `T+L` to `T`.
    - Let's verify:
        - Series `S`: [S0, S1, S2, ...]
        - `S.shift(-1)`: [S1, S2, ...] (Value at index 0 becomes S1).
        - So if we correlate `Benchmark` with `Ticker.shift(-L)`, we are correlating `Benchmark[0]` with `Ticker[L]`.
        - Correct.
    - We will apply this shift before joining/correlating.

## Implementation Steps
1.  Update `src/analysis.py` functions to accept `lag`.
2.  Apply `ticker_series = ticker_series.shift(-lag)` before aligning with benchmark.
3.  expose configurable `Lag` input in the Dashboard.
