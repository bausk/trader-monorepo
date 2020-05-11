import fetch from 'isomorphic-unfetch';
import { FRONTEND_ROOT } from './frontendRoutes';
import { BACKEND_ROOT } from './backendRoutes';

const isServer = typeof window === 'undefined';

const request = async (method, url, options) => {
    try {
        const _url = new URL(url);
        if (options.params) {
            _url.search = new URLSearchParams(options.params).toString();
        }
        const res = await fetch(
            _url,
            {
                method,
                ...(options.cookie ? {
                    headers: {
                        cookie: options.cookie,
                    },
                  }
                : (options.token ? {
                    headers: {
                        Authorization: `Bearer ${options.token}`
                    }
                } : {})),
                body: options.data && JSON.stringify(options.data)
            }
        );
        if (res.ok) {
            const result = await res.json();
            return result;
        }
        console.warn(res);
        throw new Error(res.status);
    }
    catch (e) {
        console.warn(e);
        throw e;
    }
    
};

export const fetchFrontend = {
    delete: async (url, cookie = '') => await request('DELETE', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
    get: async (url, cookie = '') => await request('GET', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
    put: async (url, cookie = '') => await request('PUT', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
    post: async (url, cookie = '') => await request('POST', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
  };

export const fetchBackend = {
    delete: async (url, token, data = null) => await request('DELETE', `${BACKEND_ROOT}${url}`, { token, data }),
    get: async (url, token, params = null) => await request('GET', `${BACKEND_ROOT}${url}`, { token, params }),
    put: async (url, token, data = null) => await request('PUT', `${BACKEND_ROOT}${url}`, { token, data }),
    post: async (url, token, data = null) => await request('POST', `${BACKEND_ROOT}${url}`, { token, data }),
  };

export const authenticatedFetchCreator = (rootStore, fetcher, endpoint) => {
    return function* (data) {
        let fetchAddress = endpoint;
        if (endpoint instanceof Function) {
            fetchAddress = endpoint(data);
        }
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetcher(fetchAddress, token, data);
            return result;
        } catch (error) {
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    };
};