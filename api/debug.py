from aiohttp import web
import ptvsd
ptvsd.enable_attach()

from entrypoint import *


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
