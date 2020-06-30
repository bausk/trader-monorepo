import config from 'lib/config';

const routes = {
    SOURCES: '/sources',
    SESSIONS_DATA: (id) => `/sessions/${id}`,
    STRATEGIES: '/strategies',
}

export default routes;

export const BACKEND_ROOT = config.BACKEND_ROOT;