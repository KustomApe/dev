from strategy import BaseStrategy
import pandas as pd

class SMACrossoverStrategy(BaseStrategy):
    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        if self.data is None or self.data.empty:
            return
        
        # Calculate moving averages
        short_sma = self.data['close'].rolling(window=self.short_window).mean()
        long_sma = self.data['close'].rolling(window=self.long_window).mean()
        
        # Generate signals: 1 when short > long, -1 when short < long
        self.signals = pd.Series(0, index=self.data.index)
        
        # Signal is 1 (Buy) when short SMA crosses above long SMA
        # Signal is -1 (Sell) when short SMA crosses below long SMA
        
        # This is a simple implementation: 1 if short > long else -1
        # We only want to signal CHANGING positions
        
        current_signal = 0
        for i in range(len(self.data)):
            if pd.isna(short_sma.iloc[i]) or pd.isna(long_sma.iloc[i]):
                continue
            
            if short_sma.iloc[i] > long_sma.iloc[i] and current_signal <= 0:
                self.signals.iloc[i] = 1
                current_signal = 1
            elif short_sma.iloc[i] < long_sma.iloc[i] and current_signal >= 0:
                self.signals.iloc[i] = -1
                current_signal = -1
        
        return self.signals
