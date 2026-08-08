import yfinance as yf
import pandas as pd
from datetime import datetime
import os

class CurrencyConverter:
    def __init__(self, base_currency='GBP'):
        self.base_currency = base_currency
        self._cache = {}  # (from_currency, to_currency) -> DataFrame

    def get_rate(self, from_currency, to_currency, date):
        if from_currency == to_currency:
            return 1.0

        pair = f"{from_currency}{to_currency}=X"
        
        if pair not in self._cache:
            # Fetch historical data. We fetch a wide range to minimize calls.
            # Using 'max' period might be overkill but ensures we have everything.
            # Alternatively, we could fetch from the start of the year of the requested date.
            try:
                ticker = yf.Ticker(pair)
                hist = ticker.history(period="max")
                if hist.empty:
                    # Some pairs might not exist in this direction, try inverse
                    inv_pair = f"{to_currency}{from_currency}=X"
                    if inv_pair not in self._cache:
                        inv_ticker = yf.Ticker(inv_pair)
                        inv_hist = inv_ticker.history(period="max")
                        if not inv_hist.empty:
                            inv_hist['Close'] = 1.0 / inv_hist['Close']
                            self._cache[pair] = inv_hist
                        else:
                            self._cache[pair] = pd.DataFrame()
                    else:
                        # If inverse already exists, use it
                        inv_hist = self._cache[inv_pair]
                        if not inv_hist.empty:
                            hist = inv_hist.copy()
                            hist['Close'] = 1.0 / hist['Close']
                            self._cache[pair] = hist
                        else:
                            self._cache[pair] = pd.DataFrame()
                else:
                    self._cache[pair] = hist
            except Exception as e:
                print(f"Error fetching rate for {pair}: {e}")
                self._cache[pair] = pd.DataFrame()

        hist = self._cache[pair]
        if hist.empty:
            return None

        # Ensure index is timezone-naive for comparison
        if hist.index.tz is not None:
            hist.index = hist.index.tz_localize(None)
        
        date_obj = pd.to_datetime(date).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find the closest date (exact or previous)
        try:
            # get_indexer with method='pad' finds the last index <= date_obj
            idx = hist.index.get_indexer([date_obj], method='pad')[0]
            if idx == -1:
                # If date is before any data, try next available
                idx = hist.index.get_indexer([date_obj], method='backfill')[0]
            
            if idx != -1:
                return hist.iloc[idx]['Close']
        except Exception:
            return None
        
        return None

    def convert(self, amount, from_currency, date):
        rate = self.get_rate(from_currency, self.base_currency, date)
        if rate is not None:
            return amount * rate
        return None
