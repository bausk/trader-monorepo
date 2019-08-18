from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
from trader import Trader


trader = Trader()
trader.setup()
app = trader.app

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
