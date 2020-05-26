from .abstract_source import AbstractSource


class LiveKunaSource(AbstractSource):
    latest_endpoint = "https://kuna.io/api/v2/trades?market={currency}"

    @classmethod
    async def get_latest(cls):
        return ['kuna results']
        raise NotImplementedError('Implement get_availability_intervals')


class LiveCryptowatchSource(AbstractSource):
    latest_endpoint = "https://api.cryptowat.ch/markets/gdax/{currency}/trades?limit={limit}&since={after}"

    @classmethod
    async def get_latest(cls):
        return ['cryptowatch results']
        raise NotImplementedError('Implement get_availability_intervals')
