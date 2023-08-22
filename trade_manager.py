from bfxapi import Client
from bfxapi.types import Order, Position

from typing import List


class TradeManager():
    orders: List[Order] = []
    positions: List[Position]
    symbol: str

    def __init__(self, client: Client, symbol: str) -> None:
        self.client = client
        self.symbol = symbol

    async def load_orders(self):
        orders = self.client.rest.auth.get_orders(symbol=self.symbol)
        for order in orders:
            if order not in self.orders:
                self.orders.append(order)

    async def load_positions(self):
        positions = self.client.rest.auth.get_positions()
        for position in positions:
            if position not in self.positions and position.symbol == self.symbol:
                self.positions.append(position)
