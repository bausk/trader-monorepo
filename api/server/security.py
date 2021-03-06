import aiohttp
from aiohttp.web import Request
from aiohttp import web
import jwt
import os
import json
from secrets_management.manage import (
    get_environment,
)


JWT_ALGORITHM = "RS256"


async def get_jwks(AUTH0_DOMAIN):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json") as resp:
            JWKS = await resp.json()
    return JWKS


class PublicKeyError(Exception):
    pass


class PermissionDenied(Exception):
    pass


async def get_middleware():
    params = {}
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
    API_AUDIENCE = os.environ.get("API_AUDIENCE")
    assert (
        AUTH0_DOMAIN
    ), "Auth0 server must be specified in AUTH0_DOMAIN environment variable"
    assert (
        API_AUDIENCE
    ), "Auth0 audience must be specified in API_AUDIENCE environment variable"

    # Fetch public key on startup
    params["JWKS"] = await get_jwks(AUTH0_DOMAIN)

    async def validate_header(unverified_header):
        JWKS = params["JWKS"]
        for _ in range(4):
            try:
                for key in JWKS["keys"]:
                    if key["kid"] == unverified_header["kid"]:
                        return {
                            "kty": key["kty"],
                            "kid": key["kid"],
                            "use": key["use"],
                            "n": key["n"],
                            "e": key["e"],
                        }
                    else:
                        raise PublicKeyError()
            except (KeyError, PublicKeyError):
                new_jwks = await get_jwks(AUTH0_DOMAIN)
                if new_jwks == JWKS:
                    return None
                JWKS = new_jwks

    @web.middleware
    async def auth_middleware(request, handler):
        request.user = None
        try:
            token = request.headers.get("authorization", None).split(" ")[1]
            if token == "TEST" and get_environment() == "development":
                request.user = {
                    "name": "Test",
                    "permissions": ["read:live", "read:history"],
                }
                return await handler(request)
            unverified_header = jwt.get_unverified_header(token)
        except Exception:
            return await handler(request)
        rsa_key = await validate_header(unverified_header)
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
                    algorithms=[JWT_ALGORITHM],
                    audience=API_AUDIENCE,
                    issuer=f"https://{AUTH0_DOMAIN}/",
                )
            except jwt.ExpiredSignatureError:
                return web.json_response({"message": "token is expired"}, status=401)
            except (jwt.InvalidAudienceError, jwt.InvalidIssuerError):
                return web.json_response(
                    {
                        "message": "Incorrect claims, please check the audience and issuer"
                    },
                    status=401,
                )
            except Exception:
                return web.json_response(
                    {"message": "Unable to parse authentication token."}, status=401
                )

            request.user = payload
        return await handler(request)

    return auth_middleware


class Permissions:
    READ = "read:live"
    READ_LIVE = "read:live"
    READ_HISTORY = "read:history"
    WRITE_OBJECTS = "read:live"
    WRITE_LIVE = "write:live"
    WRITE_HISTORY = "write:history"


async def check_permission(req: Request, permission) -> None:
    try:
        user_permissions = req.user["permissions"]
        if permission in user_permissions:
            return
    except Exception:
        pass
    raise web.HTTPUnauthorized
