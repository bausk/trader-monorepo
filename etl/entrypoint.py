#!/usr/bin/python
from aiohttp import web
from asyncio import Queue, create_task
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
from tasks.datascraper import scrape_data, scrape_data_process


app = web.Application(debug=(__name__ != '__main__'))


async def root(request):
    return web.json_response({
        'active': app.active,
        'last_data': app.last_scraped,
        'state': app.results
        })


async def start(request):
    app.active = True
    return web.json_response({
        'active': app.active,
        'last_data': app.last_scraped,
        'state': 'working'
        })


async def stop(request):
    app.active = False
    return web.json_response({
        'active': app.active,
        'last_data': app.last_scraped,
        'state': 'stopped'
        })

async def once(request):
    await scrape_data(app)
    return web.json_response({
        'active': app.active,
        'last_data': app.last_scraped
        })

async def setup(app):
    app.commands_queue = Queue()
    app.active = False
    app.results = ""
    app.last_scraped = None
    create_task(scrape_data(app))

app.add_routes([web.get('/', root),
                web.get('/start', start),
                web.get('/once', once),
                web.get('/stop', stop)])
app.on_startup.append(setup)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
