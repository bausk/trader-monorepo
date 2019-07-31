#!/usr/bin/python
from aiohttp_security.abc import AbstractAuthorizationPolicy
from aiohttp_security import check_permission, \
    is_anonymous, remember, forget, \
    setup as setup_security, SessionIdentityPolicy
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import SimpleCookieStorage, session_middleware
import aiohttp_cors
import time
import base64
import os
from cryptography import fernet
from aiohttp import web, ClientSession
from asyncio import Queue, create_task
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


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
        return identity == get_identity() and permission in ('read', 'write')


def get_identity(token=None):
    return 'admin'


async def check_identity(request):
    data = None
    if request.content_type == 'application/json':
        data = await request.json()
    else:
        data = await request.post()
    token = data.get('token', None)
    real_token = os.environ.get('USER_ACCESS_TOKEN', None)
    print(token)
    if token == real_token:
        print('performing auth')
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
    print(f'identity is {identity}')
    if identity is not None:
        if request.content_type == 'application/json':
            response = web.json_response({ 'token': identity })
            await remember(request, response, identity)
            return response
        else:
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
    await check_permission(request, 'read')
    return web.Response(body="I can listen!")


async def handler_profile(request):
    if await is_anonymous(request):
        raise web.HTTPUnauthorized()
    url = 'https://api.github.com/users/bausk'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            data = await resp.json()
            return web.json_response(data)


async def handler_speak(request):
    await check_permission(request, 'write')
    return web.Response(body="I can speak!")


def make_app():
    app = web.Application()
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    client_url = os.environ.get('CLIENT_URL', None)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    login = app.router.add_resource("/login")
    cors.add(login.add_route("POST", handler_login))
    root = app.router.add_resource("/")
    cors.add(root.add_route("GET", handler_root))
    cors.add(root.add_route("POST", handler_root))
    listen = app.router.add_resource("/listen")
    cors.add(listen.add_route("GET", handler_listen))

    # add the routes
    app.add_routes([
        web.get('/logout', handler_logout),
        web.get('/profile', handler_profile),
        web.get('/speak', handler_speak)])

    # set up policies
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleJack_AuthorizationPolicy())
    return app


app = make_app()

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
