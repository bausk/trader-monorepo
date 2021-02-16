from typing import List
from datetime import datetime, timedelta
import pandas as pd

from utils.schemas.dataflow_schemas import (
    IndicatorSchema,
    SignalSchema,
)
from utils.schemas.response_schemas import InputMarketDataSchema, PricepointSchema
from parameters.enums import IndicatorsEnum, SignalResultsEnum


def calculate_valid_timedelta(data: List[PricepointSchema]) -> timedelta:
    """
    Assuming list sorted by time, calculates length of time
    between first valid price point and end of list
    """
    if len(data) < 2:
        return timedelta(0)
    start_of_valid = data[-1]
    for record in data:
        if record.price is None:
            continue
        else:
            start_of_valid = record
            break
    return data[-1].time - start_of_valid.time


def check_is_good_for_signal(data):
    if calculate_valid_timedelta(data) < timedelta(minutes=5):
        return False
    return True


def calculate_indicators(
    market_data: List[InputMarketDataSchema],
) -> List[IndicatorSchema]:
    """calculate_indicator:
    Transform streams of market data into an list of indicators calculated from that data.
    Returns two indicators, one for buy and one for sell/close position.
    """

    no_op = IndicatorSchema(label="None", indicator=[])
    if not all(map(lambda x: check_is_good_for_signal(x.ticks), market_data)):
        return [no_op, no_op]

    min_ask_bid_ratio = 0.0035
    disregard_bars_count: int = 10
    rolling_indicator_window: str = "180s"

    primary_data = market_data[0]
    secondary_data = market_data[0]
    # Convert Pydantic lists to dataframes
    primary_dataframe = pd.DataFrame([x.dict() for x in primary_data])
    primary_dataframe["Time"] = pd.to_datetime(primary_dataframe.time, unit="s")
    primary_dataframe.set_index("Time", inplace=True)
    primary_dataframe.sort_index(inplace=True)

    secondary_dataframe = pd.DataFrame([x.dict() for x in secondary_data])
    secondary_dataframe["Time"] = pd.to_datetime(secondary_dataframe.time, unit="s")
    secondary_dataframe.set_index("Time", inplace=True)
    secondary_dataframe.sort_index(inplace=True)

    primary_without_latest = primary_dataframe["price"].shift(disregard_bars_count)
    secondary_without_latest = secondary_dataframe["price"].shift(disregard_bars_count)
    coefficients = secondary_without_latest / primary_without_latest

    pseudo_spread_secondary = secondary_dataframe["price"] * min_ask_bid_ratio

    # Calculate inter-market slip difference and get indicating list
    arbitrage_difference = (
        primary_dataframe["price"] * coefficients
    ) - secondary_dataframe["price"]
    arbitrage_indicator = (arbitrage_difference / pseudo_spread_secondary).dropna()

    # Disregard noise values (x < 1.5)
    arbitrage_indicator.loc[arbitrage_indicator < 1.5] = 0

    rolling_buy_indicator: pd.Series = arbitrage_indicator.rolling(
        rolling_indicator_window
    ).sum()
    sell_difference = (primary_dataframe["price"] * coefficients) - secondary_dataframe[
        "price"
    ]
    sell_indicator = (sell_difference / pseudo_spread_secondary).dropna()
    sell_indicator.loc[sell_indicator > -0.8] = 0
    rolling_sell_indicator: pd.Series = sell_indicator.rolling(
        rolling_indicator_window
    ).sum()
    buy_indicator = IndicatorSchema(
        label=IndicatorsEnum.buy_indicator,
        indicator=[
            dict(timestamp=x, value=y) for x, y in rolling_buy_indicator.items()
        ],
    )
    sell_indicator = IndicatorSchema(
        label=IndicatorsEnum.sell_indicator,
        indicator=[
            dict(timestamp=x, value=y) for x, y in rolling_sell_indicator.items()
        ],
    )
    return [buy_indicator, sell_indicator]


def calculate_signal(indicators: List[IndicatorSchema]) -> SignalSchema:

    signal_threshold_buy: int = 8
    signal_threshold_sell: int = -5
    ts = datetime.now()

    no_op = SignalSchema(
        timestamp=ts,
        direction=SignalResultsEnum.NO_DATA,
        value=0.0,
    )

    if any(len(i.indicator) == 0 for i in indicators):
        return no_op
    buy = indicators[0].indicator[-1]
    sell = indicators[1].indicator[-1]
    sell_signal = sell.value < signal_threshold_sell
    buy_signal = buy.value > signal_threshold_buy
    traceback = [buy.dict(), sell.dict()]
    if sell_signal:
        return SignalSchema(
            timestamp=ts,
            direction=SignalResultsEnum.SELL_ALL,
            value=round(sell.value, 2),
            traceback=traceback,
        )
    if buy_signal:
        return SignalSchema(
            timestamp=ts,
            direction=SignalResultsEnum.BUY_ALL,
            value=round(buy.value, 2),
            traceback=traceback,
        )

    return SignalSchema(
        timestamp=ts,
        direction=SignalResultsEnum.AMBIGUOUS,
        value=0.0,
        traceback=traceback,
    )
