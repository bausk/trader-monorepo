from typing import List
from utils.sources.abstract_source import AbstractSource
from dbmodels.source_models import ResourceSchema
from parameters.enums import SourcesEnum
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
    SourcesEnum.bigquery: BigquerySource,
}


def select_live_sources(resource: ResourceSchema) -> List[AbstractSource]:
    return [
        LIVE_SOURCES.get(resource.primary_live_source_model.typename)(),
        LIVE_SOURCES.get(resource.secondary_live_source_model.typename)(),
    ]


def select_backtest_sources(
    backtest_session: BacktestSessionSchema,
) -> List[AbstractSource]:
    if backtest_session.backtest_type == "test":
        return [TestPrimaryBacktestSource(), TestSecondaryBacktestSource()]
    return []
