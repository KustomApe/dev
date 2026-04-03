import pandas as pd
import numpy as np

def calculate_metrics(results: dict):
    trades = results['trade_history']
    equity_curve = results['equity_curve']
    
    if trades.empty:
        return {
            "Total Trades": 0,
            "Net Profit": 0,
            "Win Rate": 0,
            "Max Drawdown": 0
        }

    net_profit = trades['pnl'].sum()
    win_rate = (trades['pnl'] > 0).mean() * 100
    total_trades = len(trades)
    
    # Drawdown
    equity_curve['peak'] = equity_curve['equity'].cummax()
    equity_curve['drawdown'] = (equity_curve['equity'] - equity_curve['peak']) / equity_curve['peak']
    max_drawdown = equity_curve['drawdown'].min() * 100
    
    return {
        "Total Trades": total_trades,
        "Net Profit": round(net_profit, 2),
        "Win Rate (%)": round(win_rate, 2),
        "Max Drawdown (%)": round(max_drawdown, 2)
    }
