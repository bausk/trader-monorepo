from aiohttp import web


async def create_streaming_response(request, iterator):
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={"Content-Type": "text/plain"},
    )
    await response.prepare(request)
    async for line in iterator:
        await response.write(line.encode("utf-8"))

    await response.write_eof()
    return response
