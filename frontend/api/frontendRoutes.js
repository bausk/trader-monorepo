import config from 'lib/config';

const routes = {
    HOME: '/',
    LOGIN: '/api/login',
    GETTOKEN: '/api/gettoken',
    ME: '/api/me',
    LOGOUT: '/api/logout',

    EXPLORE: '/explore',
    EXPLORE_RESOURCE: '/exploreResource',
    EXPLORE_NEW: '/explore/new',
    RESOURCE_NEW: '/explore/newResource',
    MODEL: '/model',
    MODEL_NEW: '/model/new',
    OPTIMIZE: '/optimize',
    TRADE: '/trade',
    ABOUT: '/about',
    PROFILE: '/profile',
    SERVERPROFILE: '/advanced/ssr-profile',
}

export default routes;

export const FRONTEND_ROOT = config.FRONTEND_ROOT;