import enum

class OrderExecutorsEnum(str, enum.Enum):
    live = 'live'
    backtest = 'backtest'
