from parameters.enums import SignalResultsEnum
from utils.schemas.dataflow_schemas import CalculationSchema
from utils.processing.async_queue import _ProcQueue


class BacktestTrader:
    def __init__(self, tsdb_pool, session_id):
        self.latest_id = 0
        self.arrived = {}
        self.tsdb_pool = tsdb_pool
        self.session_id = session_id
        self._balance = 1000.0
        self._trades = []
        self._current_position = None

    async def _write(self, data):
        return 1

    async def _trade(self, current_result: CalculationSchema):
        signal = current_result.signal.direction
        signal_value = current_result.signal.value
        price_point = current_result.market_inputs[1].ticks[-1].price
        if signal in (SignalResultsEnum.BUY_ALL, SignalResultsEnum.SELL_ALL):
            print(f'>>> TRADE {signal} {signal_value}@{price_point}')

    async def start_trader(
        self,
        trading_queue: _ProcQueue,
    ):
        print(f'Trader Session ID: {self.session_id}')

        while True:
            signal_result: CalculationSchema = await trading_queue.coro_get()
            if signal_result is None:
                await trading_queue.coro_put(None)
                print('Trader exit')
                return
            try:
                self.arrived[signal_result.increasing_id] = signal_result
                if signal_result.increasing_id - self.latest_id == 1:
                    while True:
                        candidate_index = self.latest_id + 1
                        if (candidate_index not in self.arrived):
                            break
                        await self._trade(self.arrived[candidate_index])
                        self.latest_id = candidate_index
                        del self.arrived[candidate_index]
            except Exception as e:
                print(e)
                pass
