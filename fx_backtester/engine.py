import pandas as pd
from typing import List, Dict

class Backtester:
    def __init__(self, initial_balance: float = 10000.0, commission: float = 0.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.commission = commission
        self.positions = []
        self.trade_history = []
        self.equity_curve = []

    def run(self, df: pd.DataFrame, signals: pd.Series, tp_pips: float = None, sl_pips: float = None):
        self.balance = self.initial_balance
        self.positions = []
        self.trade_history = []
        self.equity_curve = []
        
        current_position = None
        
        for i in range(len(df)):
            timestamp = df.index[i]
            price = df['close'].iloc[i]
            high = df['high'].iloc[i]
            low = df['low'].iloc[i]
            signal = signals.iloc[i]
            
            # Update equity curve
            current_equity = self.balance
            if current_position:
                # Use current close for equity calculation
                pnl = (price - current_position['entry_price']) * current_position['size'] * current_position['direction']
                current_equity += pnl
            self.equity_curve.append({'timestamp': timestamp, 'equity': current_equity})
            
            # Exit logic (Reversal, TP, or SL)
            if current_position:
                should_exit = False
                exit_reason = "Signal"
                
                # Check for Signal Reversal
                if current_position['direction'] == 1 and signal == -1:
                    should_exit = True
                elif current_position['direction'] == -1 and signal == 1:
                    should_exit = True
                
                # Check for TP/SL
                if not should_exit:
                    if current_position['direction'] == 1: # Long
                        if tp_pips and high >= current_position['entry_price'] + (tp_pips * 0.0001):
                            should_exit = True
                            price = current_position['entry_price'] + (tp_pips * 0.0001)
                            exit_reason = "TP"
                        elif sl_pips and low <= current_position['entry_price'] - (sl_pips * 0.0001):
                            should_exit = True
                            price = current_position['entry_price'] - (sl_pips * 0.0001)
                            exit_reason = "SL"
                    else: # Short
                        if tp_pips and low <= current_position['entry_price'] - (tp_pips * 0.0001):
                            should_exit = True
                            price = current_position['entry_price'] - (tp_pips * 0.0001)
                            exit_reason = "TP"
                        elif sl_pips and high >= current_position['entry_price'] + (sl_pips * 0.0001):
                            should_exit = True
                            price = current_position['entry_price'] + (sl_pips * 0.0001)
                            exit_reason = "SL"
                
                if should_exit:
                    pnl = (price - current_position['entry_price']) * current_position['size'] * current_position['direction']
                    self.balance += pnl - self.commission
                    self.trade_history.append({
                        'entry_time': current_position['entry_time'],
                        'exit_time': timestamp,
                        'entry_price': current_position['entry_price'],
                        'exit_price': price,
                        'direction': current_position['direction'],
                        'pnl': pnl - self.commission,
                        'reason': exit_reason
                    })
                    current_position = None
            
            # Entry logic
            if not current_position:
                if signal == 1: # Buy
                    current_position = {
                        'entry_time': timestamp,
                        'entry_price': price,
                        'direction': 1,
                        'size': 1000
                    }
                    self.balance -= self.commission
                elif signal == -1: # Sell
                    current_position = {
                        'entry_time': timestamp,
                        'entry_price': price,
                        'direction': -1,
                        'size': 1000
                    }
                    self.balance -= self.commission

        return self.get_results()

    def get_results(self):
        return {
            'trade_history': pd.DataFrame(self.trade_history),
            'equity_curve': pd.DataFrame(self.equity_curve),
            'final_balance': self.balance
        }
