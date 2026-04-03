import pandas as pd
import requests
import os
from typing import Optional

class DataProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_fx_intraday(self, from_symbol: str, to_symbol: str, interval: str = "5min", outputsize: str = "full") -> pd.DataFrame:
        """
        Fetches FX intraday data from Alpha Vantage.
        """
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key,
            "datatype": "json"
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        key = f"Time Series FX ({interval})"
        if key not in data:
            print(f"DEBUG: API Response: {data}")
            raise ValueError(f"Error fetching data: {data.get('Error Message', data.get('Note', 'Unknown error'))}")
        
        df = pd.DataFrame.from_dict(data[key], orient='index')
        df.index = pd.to_datetime(df.index)
        df.columns = ["open", "high", "low", "close"]
        df = df.astype(float)
        df = df.sort_index()
        return df

    def generate_sample_data(self, symbol: str, periods: int = 500) -> pd.DataFrame:
        """
        Generates synthetic data for testing purposes.
        """
        import numpy as np
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='5min')
        close = 1.10 + np.cumsum(np.random.normal(0, 0.001, periods))
        open_ = close + np.random.normal(0, 0.0005, periods)
        high = np.maximum(open_, close) + np.random.uniform(0, 0.0005, periods)
        low = np.minimum(open_, close) - np.random.uniform(0, 0.0005, periods)
        
        df = pd.DataFrame({
            "open": open_,
            "high": high,
            "low": low,
            "close": close
        }, index=dates)
        return df

    def save_to_csv(self, df: pd.DataFrame, file_path: str):
        df.to_csv(file_path)

    def load_from_csv(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        return df
