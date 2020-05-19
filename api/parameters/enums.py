import enum


class StrategyTypesEnum(str, enum.Enum):
    interexchangearbitrage = "interexchangearbitrage"
    signalbased = "signalbased"


class OrderExecutorsEnum(str, enum.Enum):
    live = 'live'
    backtest = 'backtest'


class StrategiesEnum(str, enum.Enum):
    monitor = 'monitor'
