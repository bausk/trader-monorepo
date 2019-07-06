import ptvsd
ptvsd.enable_attach()

from entrypoint import *

if __name__ == '__main__':
    print('running in debug mode')
    app.run(host='0.0.0.0', port=8000)
