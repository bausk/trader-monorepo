#!/usr/bin/python
import time
import base64
import os
from cryptography import fernet
from aiohttp import web
from asyncio import Queue, create_task
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup, get_session
from aiohttp_security import check_permission, \
    is_anonymous, remember, forget, \
    setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy


# Demo authorization policy for only one user.
# User 'jack' has only 'listen' permission.
# For more complicated authorization policies see examples
# in the 'demo' directory.
class SimpleJack_AuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        if identity == get_identity():
            return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return identity == get_identity() and permission in ('listen',)


def get_identity(token=None):
    return 'admin'


async def check_identity(request):
    data = await request.post()
    token = data['token']
    real_token = os.environ.get('USER_ACCESS_TOKEN', None)
    if token == real_token:
        return get_identity(token)
    else:
        return None


async def handler_root(request):
    is_logged = not await is_anonymous(request)
    return web.Response(text='''<html><head></head><body>
            Login with access token<br /><br />
            <form action="/login" method="post">
            <input type="text" id="token" name="token" type="text" value="" autofocus /><br />
            <input type="submit" />
            </form>
            
            <a href="/logout">Log me out</a><br /><br />
            Check my permissions,
            when i'm logged in and logged out.<br />
            <a href="/listen">Can I listen?</a><br />
            <a href="/speak">Can I speak?</a><br />
        </body></html>''', content_type='text/html')


async def handler_login(request):
    identity = await check_identity(request)
    if identity is not None:
        redirect_response = web.HTTPFound('/')
        await remember(request, redirect_response, identity)
        raise redirect_response
    else:
        raise web.HTTPUnauthorized()


async def handler_logout(request):
    redirect_response = web.HTTPFound('/')
    await forget(request, redirect_response)
    raise redirect_response


async def handler_listen(request):
    await check_permission(request, 'listen')
    return web.Response(body="I can listen!")


async def handler_speak(request):
    await check_permission(request, 'speak')
    return web.Response(body="I can speak!")


def make_app():
    #
    # WARNING!!!
    # Never use SimpleCookieStorage on production!!!
    # It’s highly insecure!!!
    #

    # make app
    app = web.Application()
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))

    # add the routes
    app.add_routes([
        web.get('/', handler_root),
        web.post('/login', handler_login),
        web.get('/logout', handler_logout),
        web.get('/listen', handler_listen),
        web.get('/speak', handler_speak)])

    # set up policies
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleJack_AuthorizationPolicy())
    return app

app = make_app()

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
