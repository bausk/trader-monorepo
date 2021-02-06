from typing import List
import asyncio
from datetime import datetime, timedelta
from janus import Queue
import pandas as pd

from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import (
    ProcessTaskSchema,
    SignalResultSchema,
    PrimitivesSchema,
)
from utils.schemas.request_schemas import DataRequestSchema
from utils.schemas.response_schemas import PricepointSchema
from utils.timeseries.constants import DATA_TYPES
from parameters.enums import SignalResultsEnum
from utils.timeseries.timescale_utils import get_prices


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


def calculate_signal(
    primary_data: List[PricepointSchema], secondary_data: List[PricepointSchema]
) -> SignalResultSchema:

    result = SignalResultSchema(
        direction=SignalResultsEnum.NO_DATA,
        value=0.0,
        timestamp=datetime.now(),
        primitives=[],
    )
    if not all(
        [
            check_is_good_for_signal(primary_data),
            check_is_good_for_signal(secondary_data),
        ]
    ):
        return result

    min_ask_bid_ratio = 0.0035
    signal_threshold_buy: int = 8
    signal_threshold_sell: int = -5
    disregard_bars_count: int = 10
    rolling_indicator_window: str = "180s"

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

    weighted_arbitrage_indicator = arbitrage_indicator.rolling(
        rolling_indicator_window
    ).sum()
    sell_difference = (primary_dataframe["price"] * coefficients) - secondary_dataframe[
        "price"
    ]
    sell_indicator = (sell_difference / pseudo_spread_secondary).dropna()
    sell_indicator.loc[sell_indicator > -0.8] = 0
    weighted_sell_indicator = sell_indicator.rolling(rolling_indicator_window).sum()
    result.primitives = [
        [
            {"timestamp": x[0], "value": x[1]}
            for x in weighted_arbitrage_indicator.items()
        ],
        [{"timestamp": x[0], "value": x[1]} for x in weighted_sell_indicator.items()],
    ]

    if len(weighted_arbitrage_indicator) == 0 or len(weighted_sell_indicator) == 0:
        return result
    sell_signal = weighted_sell_indicator.iloc[-1].item() < signal_threshold_sell
    buy_signal = weighted_arbitrage_indicator.iloc[-1].item() > signal_threshold_buy
    if sell_signal:
        result.direction = SignalResultsEnum.SELL_ALL
        result.value = round(weighted_sell_indicator.iloc[-1], 2)
        return result
    if buy_signal:
        result.direction = SignalResultsEnum.BUY_ALL
        result.value = round(weighted_arbitrage_indicator.iloc[-1], 2)
        return result
    result.direction = SignalResultsEnum.AMBIGUOUS
    return result
