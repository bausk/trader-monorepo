from handlers import handler_root, handler_login, handler_logout, handler_listen, handler_profile

routes = [
    ('GET', '/',        handler_root,),
    ('GET', '/ws',      handler_root,),
    ('*',   '/login',   handler_login,),
    ('*',   '/signin',  handler_root, ),
    ('*',   '/signout', handler_logout,),
]
