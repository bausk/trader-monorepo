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
async def test(request):
    print('CONSOLE')
    return json({
        'hello': 'world11',
        'state': app.some_state
        })


@app.route('/bigquery')
async def test(request):
    print('CONSOLE')
    return json({
        'hello': 'bigquery',
        'state': app.results
        })

@app.listener('before_server_start')
async def setup(app, loop):    
    app.processor_queue = Queue(loop=loop)
    app.some_state = {}
    app.results = ""
    app.add_task(scrape_data(app))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
