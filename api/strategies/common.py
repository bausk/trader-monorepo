from typing import Type
from dbmodels.strategy_models import StrategySchema
from dbmodels.strategy_params_models import LiveParamsSchema
from parameters.enums import StrategiesEnum

from strategies.monitor_strategy import monitor_strategy_executor


def select_strategy_executor(strategy: Type[StrategySchema]):
    config: LiveParamsSchema = strategy.config_json
    executors = {
        StrategiesEnum.monitor: monitor_strategy_executor,
    }
    return executors.get(config.strategy_name)
