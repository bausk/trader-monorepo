from typing import List
from utils.timeseries.constants import SOURCES_TO_DATATYPES_MAP
from utils.sources.abstract_source import AbstractSource
from dbmodels.source_models import ResourceSchema, SourceSchema
from parameters.enums import BacktestTypesEnum, SourcesEnum
from .bigquery_source import BigquerySource
from .live_sources import LiveCoinbaseSource, LiveKunaSource, LiveCryptowatchSource
from .mock_sources.test_arbitrage_sources import (
    TestPrimaryBacktestSource,
    TestSecondaryBacktestSource,
)
from dbmodels.session_models import BacktestSessionSchema


LIVE_SOURCES = {
    SourcesEnum.kunaio: LiveKunaSource,
    SourcesEnum.cryptowatch: LiveCryptowatchSource,
    SourcesEnum.coinbase: LiveCoinbaseSource,
}


def select_live_sources(resource: ResourceSchema) -> List[AbstractSource]:
    return [
        LIVE_SOURCES.get(resource.primary_live_source_model.typename)(),
        LIVE_SOURCES.get(resource.secondary_live_source_model.typename)(),
    ]


BACKTEST_SOURCES = {
    SourcesEnum.bigquery: BigquerySource,
}


def select_backtest_sources(
    backtest_session: BacktestSessionSchema,
) -> List[AbstractSource]:
    """Using configurations of sources referenced by session DB model,
    selects source class that corresponds to source typename,
    instantiates source instances, adds config to them and returns
    list of instances.

    Args:
        backtest_session (BacktestSessionSchema): freshly created backtest session

    Returns:
        List[AbstractSource]: list of backtesting sources that implement
        cache() and get_latest()
    """
    if backtest_session.backtest_type == BacktestTypesEnum.test:
        return [TestPrimaryBacktestSource(), TestSecondaryBacktestSource()]
    sources: List[SourceSchema] = backtest_session.backtest_sources
    instantiated_sources = []
    for order, source in enumerate(sources):
        data_type = SOURCES_TO_DATATYPES_MAP[order]
        source.config_json["data_type"] = data_type
        assert source.config_json["table_name"] is not None
        assert source.config_json["label"] is not None
        source_instance = BACKTEST_SOURCES.get(source.typename)()
        source_instance.config = source.config_json
        source_instance.cache_session_id = source.cache_session_id
        instantiated_sources.append(source_instance)
    return instantiated_sources
