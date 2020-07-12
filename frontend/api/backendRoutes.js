import config from 'lib/config';

const routes = {
    SOURCES: '/sources',
    SOURCE_STATS: (id) => `/sources/${id}/stats`,
    SOURCE_INTERVALS: (id) => `/sources/${id}/interval`,
    RESOURCES: '/resources',
    RESOURCE_DETAIL: (id) => `/resources/${id}`,
    SESSIONS_DATA: (id) => `/sessions/${id}`,
    STRATEGIES: '/strategies',
}

export default routes;

export const BACKEND_ROOT = config.BACKEND_ROOT;