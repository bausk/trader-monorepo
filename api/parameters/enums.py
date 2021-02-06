import enum


class StrategyTypesEnum(str, enum.Enum):
    interexchangearbitrage = "interexchangearbitrage"
    signalbased = "signalbased"


class StrategiesEnum(str, enum.Enum):
    monitor = "monitor"
    randomwalk = "randomwalk"
    arbitrage = "arbitrage"
    other = "other"


class SourcesEnum(str, enum.Enum):
    kunaio = "kunaio"
    cryptowatch = "cryptowatch"
    coinbase = "coinbase"
    bigquery = "bigquery"


class SignalResultsEnum(str, enum.Enum):
    BUY_ALL = "BUY_ALL"
    SELL_ALL = "SELL_ALL"
    AMBIGUOUS = "AMBIGUOUS"
    NO_DATA = "NO_DATA"
