from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self):
        self.data: pd.DataFrame = None
        self.signals = pd.Series()

    def set_data(self, df: pd.DataFrame):
        self.data = df

    @abstractmethod
    def generate_signals(self):
        """
        Should populate self.signals with 1 (buy), -1 (sell), or 0 (hold)
        """
        pass
