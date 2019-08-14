#!/usr/bin/python
from aiohttp_security import setup as setup_security, SessionIdentityPolicy
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_cors
import base64
from cryptography import fernet
from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path
from auth.apiAuth import SimpleAuthorizationPolicy
from handlers import handler_root, handler_login, handler_logout, handler_listen, handler_profile
from handlers.api import Api
from models.terminal import ArbitrageTerminal

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


def make_app():
    app = web.Application()
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    add = app.router.add_resource

    cors.add(add("/login").add_route("POST", handler_login))
    root = add("/")
    cors.add(root.add_route("GET", handler_root))
    cors.add(root.add_route("POST", handler_root))
    cors.add(add('/listen').add_route("GET", handler_listen))
    app.add_routes([
        web.get('/logout', handler_logout),
        web.get('/profile', handler_profile)])

    terminal = ArbitrageTerminal()
    terminal_api = Api(terminal)
    terminal_api.bind(app)
    # set up policies
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleAuthorizationPolicy())
    return app


app = make_app()

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
