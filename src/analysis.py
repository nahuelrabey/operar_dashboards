import pandas as pd
import yfinance as yf
from src import market_data

def get_daily_performance(df_prices: pd.DataFrame, target_date: pd.Timestamp) -> pd.DataFrame:
    """
    Calculates the daily performance (Close price change) for all tickers in df_prices.
    
    Args:
        df_prices: DataFrame with datetime index and ticker columns (or MultiIndex).
                   Expected to contain 'Close' prices or allow extraction of them.
        target_date: The date to calculate performance for.
        
    Returns:
        DataFrame with columns ['Ticker', 'Close', 'Prev Close', 'Change %']
    """
    if df_prices is None or df_prices.empty:
        return pd.DataFrame()

    # robust close extraction (reused from previous dashboard logic)
    close_data = _get_close_data(df_prices)
    
    if close_data.empty:
        return pd.DataFrame()

    # Normalize dates
    close_data.index = pd.to_datetime(close_data.index).normalize()
    target_date = pd.Timestamp(target_date).normalize()
    
    available_dates = close_data.index.sort_values(ascending=False)
    
    # Check if target_date exists, if not, find latest
    effective_date = target_date
    if target_date not in available_dates:
        if not available_dates.empty:
            effective_date = available_dates[0]
        else:
            return pd.DataFrame() # No dates available

    # Find previous date
    if effective_date not in available_dates:
        return pd.DataFrame() # Should not happen if we picked from available
        
    loc = available_dates.get_loc(effective_date)
    
    stats = []
    
    if loc + 1 < len(available_dates):
        prev_dt = available_dates[loc + 1]
        
        for ticker in close_data.columns:
            try:
                close_today = close_data.loc[effective_date, ticker]
                close_prev = close_data.loc[prev_dt, ticker]
                
                if pd.notna(close_today) and pd.notna(close_prev) and close_prev != 0:
                    pct_change = (close_today - close_prev) / close_prev
                    stats.append({
                        "Ticker": ticker,
                        "Close": close_today,
                        "Prev Close": close_prev,
                        "Change %": pct_change * 100
                    })
            except Exception:
                continue
    
    return pd.DataFrame(stats)

def calculate_correlations(tickers: list, benchmark_ticker: str = "GLD", period: str = "5d") -> pd.DataFrame:
    """
    Fetches 1h data for tickers and benchmark, and calculates correlation.
    """
    # Fetch CEDEARs
    df_cedears = market_data.fetch_batch_candles(tickers, period=period, interval="1h")
    
    # Fetch Benchmark (e.g. GLD US)
    # We use yf.download directly for the benchmark to ensure we get the US ticker if requested,
    # or we could use market_data if we wanted .BA suffix. 
    # The prompt implied using "GLD" (US) for "Gold Price".
    df_benchmark = yf.download(benchmark_ticker, period=period, interval="1h", auto_adjust=False, progress=False)
    
    cedear_closes = _get_close_data(df_cedears)
    benchmark_closes = _get_close_data(df_benchmark)
    
    if benchmark_closes.empty:
        return pd.DataFrame()
        
    # Benchmark might be DataFrame or Series. Ensure Series.
    if isinstance(benchmark_closes, pd.DataFrame):
         # Take first col
         benchmark_series = benchmark_closes.iloc[:, 0]
    else:
         benchmark_series = benchmark_closes

    benchmark_series = benchmark_series.rename(benchmark_ticker)
    
    if cedear_closes.empty:
        return pd.DataFrame()
        
    # Join with lsuffix to handle collisions (e.g. GLD in tickers vs GLD benchmark)
    combined = cedear_closes.join(benchmark_series, how='inner', lsuffix='_TICKER')
    
    if combined.empty or benchmark_ticker not in combined.columns:
        return pd.DataFrame()
        
    correlations = combined.corrwith(combined[benchmark_ticker])
    
    # Cleanup
    corr_df = correlations.drop(benchmark_ticker, errors='ignore').reset_index()
    corr_df.columns = ['Ticker', 'Correlation']
    corr_df = corr_df.dropna().sort_values('Correlation', ascending=False)
    
    return corr_df

def _get_close_data(df):
    """(Internal) Extracts Close prices from yfinance DataFrame."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    if isinstance(df.columns, pd.MultiIndex):
        for level in range(df.columns.nlevels):
            if 'Close' in df.columns.get_level_values(level):
                return df.xs('Close', axis=1, level=level)
    else:
        if 'Close' in df.columns:
            return df[['Close']]
            
    return pd.DataFrame()
