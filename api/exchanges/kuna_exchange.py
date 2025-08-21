import aiohttp
from .base_exchanche import BaseExchange


class KunaExchangeV3(BaseExchange):
    _base_endpoint = 'https://api.kuna.io/v3/'
    _balance_endpoint = 'auth/r/wallets'
    _orders_endpoint = ''
    _place_order_endpoint = ''

    def __init__(self, session=None) -> None:
        super().__init__()
        if session is None:
            session = aiohttp.ClientSession()

    def _sign(self, verb, uri, params=""):
        message = "{verb}|{uri}|{params}".format(verb=verb, uri=uri, params=params)
        key = self._secret_key_input.value
        h = hmac.new(key.encode(), message.encode(), hashlib.sha256)
        return h.hexdigest()

    async def _post(self):
        headers = {
            'content-type': 'application/json',

        }
        pass
