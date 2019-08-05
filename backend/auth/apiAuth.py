import os

from aiohttp_security import AbstractAuthorizationPolicy


def get_identity(token=None):
    return 'admin'


class SimpleAuthorizationPolicy(AbstractAuthorizationPolicy):
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
