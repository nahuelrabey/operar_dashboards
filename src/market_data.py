import yfinance as yf
import pandas as pd
from typing import Optional

def fetch_candles(ticker: str, period: str = "7d", interval: str = "1h", suffix: str = "") -> pd.DataFrame:
    """
    Fetches historical candle data for a given ticker.
    
    Args:
        ticker (str): The ticker symbol (e.g., "AAPL").
        period (str): The data period to download (default "7d").
        interval (str): The candle interval (default "1h").
        suffix (str): Suffix to append to the ticker (default "" for origin exchange).
                      Set to ".BA" for CEDEARs/BCBA if needed.
                      
    Returns:
        pd.DataFrame: DataFrame containing the historical data. 
                      Returns empty DataFrame on failure or no data.
    """
    full_ticker = f"{ticker}{suffix}"
    try:
        # Download data
        # auto_adjust=True handles splits/dividends automatically if preferred
        df = yf.download(full_ticker, period=period, interval=interval, progress=False, auto_adjust=False)
        
        if df.empty:
            print(f"Warning: No data found for {full_ticker}")
            return pd.DataFrame()
            
        return df
    except Exception as e:
        print(f"Error fetching data for {full_ticker}: {e}")
        return pd.DataFrame()

def fetch_batch_candles(tickers: list[str], period: str = "7d", interval: str = "1h", suffix: str = "") -> pd.DataFrame:
    """
    Fetches historical candle data for a list of tickers in batch.
    
    Args:
        tickers (list[str]): List of ticker symbols.
        period (str): The data period to download (default "7d").
        interval (str): The candle interval (default "1h").
        suffix (str): Suffix to append to the tickers (default "").
        
    Returns:
        pd.DataFrame: DataFrame containing the historical data.
                      The columns will have a MultiIndex if multiple tickers are returned.
    """
    if not tickers:
        return pd.DataFrame()
        
    full_tickers = [f"{t}{suffix}" for t in tickers] if suffix else tickers
    
    try:
        # yfinance download accepts a list of tickers string separated by space
        tickers_str = " ".join(full_tickers)
        
        # optimized batch download
        df = yf.download(tickers_str, period=period, interval=interval, group_by='ticker', auto_adjust=False, progress=True)
        
        return df
    except Exception as e:
        print(f"Error fetching batch data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Simple test
    t = "AAPL"
    print(f"Testing fetch for {t}...")
    df = fetch_candles(t)
    print(df.head())
