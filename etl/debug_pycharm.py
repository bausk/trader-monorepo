import pydevd_pycharm
pydevd_pycharm.settrace('192.168.99.1', port=5666, stdoutToServer=True, stderrToServer=True)

from entrypoint import app

if __name__ == '__main__':
    print('running in debug mode')
    app.run(host='0.0.0.0', port=8000, auto_reload=True, debug=True)
