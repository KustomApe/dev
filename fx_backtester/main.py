import sys
import os
from data_provider import DataProvider
from sample_strategy import SMACrossoverStrategy
from engine import Backtester
from metrics import calculate_metrics
from plotter import plot_results
from tabulate import tabulate

def main():
    # Configuration
    API_KEY = "3BGNH32PDTRCMDOY" # Alpha Vantage Demo or User Key
    SYMBOL_FROM = "EUR"
    SYMBOL_TO = "USD"
    INTERVAL = "5min"
    
    print(f"Starting FX Backtester for {SYMBOL_FROM}/{SYMBOL_TO} ({INTERVAL})...")
    
    # 1. Fetch Data
    provider = DataProvider(API_KEY)
    try:
        data_path = f"{SYMBOL_FROM}_{SYMBOL_TO}_{INTERVAL}.csv"
        if os.path.exists(data_path):
            print(f"Loading data from local cache: {data_path}")
            df = provider.load_from_csv(data_path)
        else:
            try:
                print("Fetching data from Alpha Vantage...")
                df = provider.fetch_fx_intraday(SYMBOL_FROM, SYMBOL_TO, interval=INTERVAL)
                provider.save_to_csv(df, data_path)
                print(f"Data saved to {data_path}")
            except Exception as e:
                print(f"API Error: {e}")
                print("Generating sample data for demonstration...")
                df = provider.generate_sample_data(f"{SYMBOL_FROM}/{SYMBOL_TO}")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Strategy
    strategy = SMACrossoverStrategy(short_window=10, long_window=30)
    strategy.set_data(df)
    signals = strategy.generate_signals()
    
    # 3. Backtest
    backtester = Backtester(initial_balance=10000, commission=0.5)
    results = backtester.run(df, signals, tp_pips=50, sl_pips=30)
    
    # 4. Metrics
    metrics = calculate_metrics(results)
    print("\n" + "="*30)
    print("      BACKTEST RESULTS")
    print("="*30)
    print(tabulate(metrics.items(), tablefmt="grid"))
    
    # 5. Visualization
    plot_results(df, results, title=f"SMA Crossover {SYMBOL_FROM}/{SYMBOL_TO}")

if __name__ == "__main__":
    main()
