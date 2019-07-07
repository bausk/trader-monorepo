from sanic import Sanic
from sanic.response import json

app = Sanic()

@app.route('/')
async def test(request):
    print('CONSOLE')
    return json({'hello': 'world10'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
