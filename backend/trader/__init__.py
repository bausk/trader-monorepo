from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import base64
from cryptography import fernet
from aiohttp import web
from view.api import TerminalApi
from taskmanager import DataManager


class Trader:
    def __init__(self):
        self.app = None
        self._api = TerminalApi()
        self._manager = DataManager()

    def create_app(self):
        app = web.Application()
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(app, EncryptedCookieStorage(secret_key))

        self._manager.setup_tasks(app)
        self._api.setup_api(app, self._manager)
        return app

    def setup(self):
        self.app = self.create_app()
