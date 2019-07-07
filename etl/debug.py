# import multiprocessing
# multiprocessing.set_start_method('spawn', True)
# import socket
import ptvsd
ptvsd.enable_attach()
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.close()


from entrypoint import app

if __name__ == '__main__':
    print('running in debug mode')    
    @app.route('/_restart')
    async def test(request):
        print('RESTARTING')
        import os, sys
        os.execv(sys.executable, [sys.executable, __file__] + sys.argv)
    
    app.run(host='0.0.0.0', port=8000, auto_reload=False, debug=True)
