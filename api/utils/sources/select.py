from parameters.enums import SourcesEnum
from .bigquery_source import BigquerySource
from .live_sources import LiveCoinbaseSource, LiveKunaSource, LiveCryptowatchSource


LIVE_SOURCES = {
    SourcesEnum.kunaio: LiveKunaSource,
    SourcesEnum.cryptowatch: LiveCryptowatchSource,
    SourcesEnum.coinbase: LiveCoinbaseSource,
    SourcesEnum.bigquery: BigquerySource,
}
