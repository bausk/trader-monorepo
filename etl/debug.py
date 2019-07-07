from entrypoint import app

flag = 0
if __name__ == '__main__':
    print('running in debug mode')
    import ptvsd
    if flag == 0:
        flag = 1
        ptvsd.enable_attach()

    app.run(host='0.0.0.0', port=8000, auto_reload=True, debug=True)
