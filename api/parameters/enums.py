import enum


class StrategyTypesEnum(str, enum.Enum):
    interexchangearbitrage = "interexchangearbitrage"
    signalbased = "signalbased"


class StrategiesEnum(str, enum.Enum):
    monitor = 'monitor'
    randomwalk = 'randomwalk'
    arbitrage = 'arbitrage'
    other = 'other'


class LiveSourcesEnum(str, enum.Enum):
    kunaio = 'kunaio'
    cryptowatch = 'cryptowatch'
