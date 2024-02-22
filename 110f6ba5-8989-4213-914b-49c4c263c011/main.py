from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR, VWAP
from surmount.data import Asset
from surmount.logging import log
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["QQQ", "XLE", "XPH"] # Technology, energy, and pharmaceutical ETFs

    @property
    def interval(self):
        return "1day" # Daily intervals for analysis

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # Only needing the ohlcv data for this strategy
        return [Asset(i) for i in self.tickers]

    def run(self, data):
        allocation_dict = {}
        total_atr = sum([ATR(i, data["ohlcv"], 14)[-1] for i in self.tickers])  # Calculate total ATR for risk management

        for ticker in self.tickers:
            # Calculate ATR and VWAP for each ticker
            atr = ATR(ticker, data["ohlcv"], 14)[-1]
            vwap = VWAP(ticker, data["ohlcv"], 30)[-1]  # Using last 30 days to calculate VWAP
            current_price = data["ohlcv"][-1][ticker]['close']

            # Setting allocation based on momentum and volume with volatility adjustment
            # High risk and speculative: positions are opened based on the stock's momentum compared to its average price and adjusted by volatility
            if current_price > vwap and atr/total_atr > 0.1:
                allocation = min(0.9, (atr/total_atr)*2)  # Aggressive allocation with a cap at 90%
            else:
                allocation = 0  # No allocation if the conditions are not met

            allocation_dict[ticker] = allocation

        log(f"Allocations: {allocation_dict}")  # Logging allocations for review
        return TargetAllocation(allocation_dict)  # Returning the target allocations based on strategy logic