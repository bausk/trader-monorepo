from aiohttp import web, ClientSession
from aiohttp_security import is_anonymous, remember, forget, check_permission

from auth.apiAuth import check_identity


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
            response = web.json_response({'token': identity})
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