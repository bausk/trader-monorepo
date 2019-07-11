from sanic import Sanic
from sanic.response import json
from asyncio import Queue
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
from tasks.datascraper import scrape_data


app = Sanic()

@app.route('/')
async def root(request):
    return json({
        'active': app.active,
        'last_data': app.last_scraped,
        'state': app.results
        })


@app.route('/start')
async def start(request):
    app.active = True
    return json({
        'active': app.active,
        'last_data': app.last_scraped,
        'state': 'working'
        })

@app.route('/stop')
async def stop(request):
    app.active = False
    return json({
        'active': app.active,
        'last_data': app.last_scraped,
        'state': 'stopped'
        })


@app.listener('before_server_start')
async def setup(app, loop):    
    app.commands_queue = Queue(loop=loop)
    app.active = True
    app.results = ""
    app.last_scraped = None
    app.add_task(scrape_data(app))

app.debug = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
