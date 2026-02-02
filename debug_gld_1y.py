import yfinance as yf
import pandas as pd

# Fetch 1Y GLD data
print("Fetching 1Y GLD data...")
df = yf.download("GLD", period="1y", interval="1d", auto_adjust=False, progress=False)

if not df.empty:
    opens = df["Open"]
    closes = df["Close"]
    
    if isinstance(opens, pd.DataFrame): opens = opens.iloc[:, 0]
    if isinstance(closes, pd.DataFrame): closes = closes.iloc[:, 0]
    
    first_open = opens.iloc[0]
    last_close = closes.iloc[-1]
    
    pct_change = (last_close / first_open - 1) * 100
    
    print(f"Start Date: {df.index[0]}")
    print(f"End Date: {df.index[-1]}")
    print(f"First Open: {first_open}")
    print(f"Last Close: {last_close}")
    print(f"Cumulative Return (Open to Close): {pct_change:.2f}%")
else:
    print("No data fetched.")
