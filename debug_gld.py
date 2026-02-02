import yfinance as yf
import pandas as pd
import datetime

# Fetch GLD data for the relevant period (last week of Jan 2026)
start_date = "2026-01-25"
end_date = "2026-02-02"

print(f"Fetching GLD data from {start_date} to {end_date}...")
df = yf.download("GLD", start=start_date, end=end_date, interval="1h", auto_adjust=False, progress=False)

print("\n--- Columns ---")
print(df.columns)

print("\n--- Head ---")
print(df.head())

print("\n--- Tail ---")
print(df.tail())

print("\n--- Close Prices around Jan 30 ---")
# Filter for Jan 30
try:
    jan30 = df.loc["2026-01-30"]
    print(jan30)
except Exception as e:
    print(f"Could not filter for Jan 30: {e}")
    
# Debug Normalization
closes = df["Close"]
if isinstance(closes, pd.DataFrame):
     closes = closes.iloc[:, 0]

first_val = closes.iloc[0]
last_val = closes.iloc[-1]
pct_change = (last_val / first_val - 1) * 100

print(f"\nFirst Value: {first_val}")
print(f"Last Value: {last_val}")
print(f"Calculated Performance: {pct_change:.2f}%")
