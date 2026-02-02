import pandas as pd
from market_data import fetch_candles
import time

def main():
    csv_file = "cedears.csv"
    try:
        df_cedears = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"File {csv_file} not found. Please run extract_cedears.py first.")
        return

    print(f"Loaded {len(df_cedears)} CEDEARs from {csv_file}")
    
    # Pick a few samples to test
    samples = df_cedears.sample(n=3)
    
    for index, row in samples.iterrows():
        ticker = row['byma_code']
        ratio = row['ratio']
        print(f"\nFetching data for {ticker} (Ratio: {ratio})...")
        
        df_prices = fetch_candles(ticker, period="1wk", interval="1h")
        
        if not df_prices.empty:
            print("Success! Last 3 records:")
            print(df_prices.tail(3))
        else:
            print("Failed to fetch data.")
            
        # Be nice to the API
        time.sleep(1)

if __name__ == "__main__":
    main()
