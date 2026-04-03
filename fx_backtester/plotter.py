import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_results(df: pd.DataFrame, results: dict, title: str = "Backtest Results"):
    equity_curve = results['equity_curve']
    trades = results['trade_history']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Plot Close Price and Trades
    ax1.plot(df.index, df['close'], label='Close Price', color='gray', alpha=0.5)
    
    if not trades.empty:
        buy_trades = trades[trades['direction'] == 1]
        sell_trades = trades[trades['direction'] == -1]
        
        ax1.scatter(buy_trades['entry_time'], buy_trades['entry_price'], marker='^', color='green', label='Buy', s=100)
        ax1.scatter(sell_trades['entry_time'], sell_trades['entry_price'], marker='v', color='red', label='Sell', s=100)
    
    ax1.set_title(f"{title} - Price and Trades")
    ax1.legend()
    ax1.grid(True)
    
    # Plot Equity Curve
    ax2.plot(equity_curve['timestamp'], equity_curve['equity'], label='Equity', color='blue')
    ax2.set_title("Equity Curve")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    try:
        plt.show()
    except Exception:
        pass
    plt.savefig("backtest_plot.png")
    print(f"Backtest plot saved to {os.getcwd()}/backtest_plot.png")
