from handlers import handler_root, handler_login, handler_logout, handler_listen, handler_profile

routes = [
    ('POST', '/',        handler_root,),
    ('GET',  '/',        handler_root,),
    ('POST', '/login',   handler_login,),
    ('GET',  '/listen',  handler_listen,),
    ('GET',  '/logout',  handler_logout,),
    ('GET',  '/profile', handler_profile,),
]
