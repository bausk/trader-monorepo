from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import base64
from cryptography import fernet
from aiohttp import web


def setup_aiohttp_security(app):
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    return app


def setup_scheduler(app, scheduler):
    scheduler.setup_tasks(app)
    return app


def setup_routes(app, routes):
    return app
