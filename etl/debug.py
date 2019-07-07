# import multiprocessing
# multiprocessing.set_start_method('spawn', True)
# import socket

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.close()


from entrypoint import app
# flag = 0
if __name__ == '__main__':
    print('running in debug mode')
    import ptvsd
    from sanic.response import json
    
    @app.route('/_attach')
    async def attach(request):
        print('ATTACHING')
        ptvsd.enable_attach()
        return json({'response': 'attached'})

    @app.route('/_restart')
    async def restart(request):
        print('RESTARTING')
        import os, sys
        os.execv(sys.executable, [sys.executable, __file__] + sys.argv)
    
    # if flag == 0:
    #     flag = 1
    #     ptvsd.enable_attach()

    app.run(host='0.0.0.0', port=8000, auto_reload=True, debug=True)
