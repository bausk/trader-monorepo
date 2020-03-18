from aiohttp import web


def create_error_middleware(overrides):
    @web.middleware
    async def error_middleware(request, handler):
        try:
            response = await handler(request)
            override = overrides.get(response.status)
            if override:
                return await override(request)
            return response
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)
            raise
        except Exception as ex:
            for override_type, override in overrides.items():
                if isinstance(ex, override_type):
                    return await override(request)
            raise

    return error_middleware
