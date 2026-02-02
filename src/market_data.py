import yfinance as yf
import pandas as pd
from typing import Optional

import os
import pickle
import hashlib

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_path(func_name, *args, **kwargs):
    """Generates a cache filename based on function usage."""
    # Create a unique key from arguments
    # We explicitly handle list arguments (like tickers) to ensure stable hashing
    arg_str = str(args) + str(kwargs)
    # Use MD5 for a short, deterministic suffix
    arg_hash = hashlib.md5(arg_str.encode()).hexdigest()
    
    # Try to make a readable part if possible (e.g. for single ticker)
    readable_part = ""
    if args and isinstance(args[0], str):
        readable_part = f"_{args[0]}"
    
    filename = f"{func_name}{readable_part}_{arg_hash}.pkl"
    return os.path.join(CACHE_DIR, filename)

def _load_from_cache(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading cache {path}: {e}")
    return None

def _save_to_cache(path, data):
    try:
        with open(path, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error saving cache {path}: {e}")

def fetch_candles(ticker: str, period: str = "7d", interval: str = "1h", suffix: str = "") -> pd.DataFrame:
    """
    Fetches historical candle data for a given ticker with caching.
    """
    cache_path = _get_cache_path("fetch_candles", ticker=ticker, period=period, interval=interval, suffix=suffix)
    cached_data = _load_from_cache(cache_path)
    if cached_data is not None:
        return cached_data

    full_ticker = f"{ticker}{suffix}"
    try:
        df = yf.download(full_ticker, period=period, interval=interval, progress=False, auto_adjust=False)
        
        if df.empty:
            print(f"Warning: No data found for {full_ticker}")
            return pd.DataFrame()
            
        _save_to_cache(cache_path, df)
        return df
    except Exception as e:
        print(f"Error fetching data for {full_ticker}: {e}")
        return pd.DataFrame()

def fetch_batch_candles(tickers: list[str], period: str = "7d", interval: str = "1h", suffix: str = "") -> pd.DataFrame:
    """
    Fetches historical candle data for a list of tickers in batch with caching.
    """
    if not tickers:
        return pd.DataFrame()
        
    cache_path = _get_cache_path("fetch_batch_candles", tickers=tuple(sorted(tickers)), period=period, interval=interval, suffix=suffix)
    cached_data = _load_from_cache(cache_path)
    if cached_data is not None:
        return cached_data

    full_tickers = [f"{t}{suffix}" for t in tickers] if suffix else tickers
    
    try:
        tickers_str = " ".join(full_tickers)
        df = yf.download(tickers_str, period=period, interval=interval, group_by='ticker', auto_adjust=False, progress=True)
        
        _save_to_cache(cache_path, df)
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
