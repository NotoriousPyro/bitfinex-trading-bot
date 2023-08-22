from bfxapi import Client
from bfxapi.types import Candle
from bfxapi.websocket.subscriptions import Candles

from collections import deque
from datetime import datetime, timedelta
from typing import List

class CandleHolder():
    candles: deque[Candle]
    client: Client
    symbol: str

    def __init__(self, client: Client, symbol: str, max_sampling_period: int) -> None:
        self.client = client
        self.symbol = symbol
        self.max_sampling_period = max_sampling_period
        self.candles = deque(maxlen=max_sampling_period)

    def on_candles_update(self, subscription: Candles, data: Candle):
        self.__update_candles__([data])

    def __update_candles__(self, candles: List[Candle]) -> None:
        for candle in candles:
            if candle not in self.candles:
                self.candles.append(candle)

    def load_candles(self):
        start_date = int((datetime.now() - timedelta(minutes=self.max_sampling_period)).timestamp())
        candles = self.client.rest.public.get_candles_hist(
            tf='1m',
            symbol=self.symbol,
            sort="+1",
            start=f"{start_date}000"
        )
        self.__update_candles__(candles)
        if not any(self.candles):
            raise ValueError("No candles.")

    def calculate_dpo(self):
        dpo_values = []
        num_candles = len(self.candles)
        period = self.max_sampling_period
        if num_candles <= period:
            period = num_candles - 2
        for i in range(period, num_candles):
            dpo = self.candles[i].close - self.candles[i - period + 2].close
            dpo_values.append(dpo)
        return dpo_values

    def calculate_hv(self, dpo: list[int]):
        hv = [close_price ** 2 for close_price in dpo]
        return (sum(hv) / len(hv)) ** 0.5

    def calculate_pc(self):
        pc_center = (self.candles[-1].high + self.candles[-1].low) / 2
        pc_low = self.candles[-1].low
        pc_percentage_diff = (pc_center - pc_low) / ((pc_center + pc_low) / 2) * 100
        return pc_center, pc_low, pc_percentage_diff
