from candle_holder import CandleHolder
from config import Config
from trade_manager import TradeManager

from bfxapi import Client, PUB_REST_HOST, PUB_WSS_HOST
from bfxapi.websocket.enums import Channel

import asyncio


tolerance = 1.5
max_sampling_period = 21
symbol = "tBTCF0:USTF0"



with open("config.json") as config:
    config = Config.model_validate_json(config.read())
    bfx = Client(**config.auth.model_dump(), rest_host=PUB_REST_HOST, wss_host=PUB_WSS_HOST)


async def on_open():
    await bfx.wss.subscribe(Channel.CANDLES, key="trade:1m:tBTCUSD")


candle_holder = CandleHolder(client=bfx, symbol=symbol, max_sampling_period=max_sampling_period)
bfx.wss.on("open", callback=on_open)
bfx.wss.on("candles_update", callback=candle_holder.on_candles_update)

trade_manager = TradeManager(client=bfx, symbol=symbol)


def should_open_trade() -> bool:
    # Calculate DPO, HV, and PC values
    dpo_values = candle_holder.calculate_dpo()
    hv_value = candle_holder.calculate_hv(dpo=dpo_values)
    _, _, pc_percentage_diff = candle_holder.calculate_pc()
    
    # Check strategy conditions
    return dpo_values[-2] < -2400 and dpo_values[-1] > dpo_values[-2] and hv_value > 25 and pc_percentage_diff < tolerance


async def main_loop():
    looped = False
    while True:
        if looped:
            await asyncio.sleep(60)
        looped = True
        await asyncio.gather(
            trade_manager.load_orders(),
            trade_manager.load_positions()
        )
        if should_open_trade():
            print("do the trade")
            pass


def main():
    candle_holder.load_candles()

    loop = asyncio.get_event_loop()
    loop.create_task(bfx.wss.start(connections=5))
    loop.create_task(main_loop())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()


if __name__ == "__main__":
    main()

