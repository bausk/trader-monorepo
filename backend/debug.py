import ptvsd
ptvsd.enable_attach()

from api import *

if __name__ == '__main__':
    app.debug = False
    app.run(host="0.0.0.0", port=3000, debug=False)
