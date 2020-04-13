import fetch from 'isomorphic-unfetch';
import { FRONTEND_ROOT } from './frontendRoutes';
import { BACKEND_ROOT } from './backendRoutes';

const isServer = typeof window === 'undefined';

const request = async (method, url, options) => {
    console.log(options);
    try {
        const res = await fetch(
            url,
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
                } : {}))
            }
        );
        if (res.ok) {
            const result = await res.json();
            return result;
        }
        console.warn(res);
        throw new Error(`could not ${method} data from ${url}`);
    }
    catch (e) {
        console.warn(e);
        throw e;
    }
    
};

export const fetchFrontend = {
    del: async (url, cookie = '') => await request('DELETE', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
    get: async (url, cookie = '') => await request('GET', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
    put: async (url, cookie = '') => await request('PUT', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
    post: async (url, cookie = '') => await request('POST', isServer ? `${FRONTEND_ROOT}${url}` : url, { cookie }),
  };

export const fetchBackend = {
    del: async (url, token) => await request('DELETE', `${BACKEND_ROOT}${url}`, { token }),
    get: async (url, token) => await request('GET', `${BACKEND_ROOT}${url}`,{ token }),
    put: async (url, token) => await request('PUT', `${BACKEND_ROOT}${url}`,{ token }),
    post: async (url, token) => await request('POST', `${BACKEND_ROOT}${url}`, { token }),
  };
