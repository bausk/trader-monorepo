import fetch from 'isomorphic-unfetch';

const isServer = typeof window === 'undefined';
const API_ROOT = 'http://localhost:3000';
const SERVICE_ROOT = 'http://localhost:5000';

const request = async (method, url, auth) => {
    return await fetch(
        url,
        {
            method,
            ...(auth.cookie ? {
                headers: {
                  cookie,
                },
              }
            : (auth.token ? {
                Authorization: `Bearer ${token}`
            } : {}))
        }
    );
};

const requests = {
    del: async (url, cookie = '') => await request(isServer ? `${API_ROOT}${url}` : url, 'DELETE', { cookie }),
    get: async (url, cookie = '') => await request(API_ROOT, 'GET', { cookie }),
    put: async (url, cookie = '') => await request(API_ROOT, 'PUT', { cookie }),
    post: async (url, cookie = '') => await request(API_ROOT, 'POST', { cookie }),
  };

const service = {
    del: async (url, token) => await request(`${SERVICE_ROOT}${url}`, 'DELETE', { token }),
    get: async (url, token) => await request(`${SERVICE_ROOT}${url}`, 'GET', { token }),
    put: async (url, token) => await request(`${SERVICE_ROOT}${url}`, 'PUT', { token }),
    post: async (url, token) => await request(`${SERVICE_ROOT}${url}`, 'POST', { token }),
  };


export const Auth = {
    gettoken: async () => {
        try {
            const res = await requests.get('/api/gettoken');
            if (res.ok) {
                const { accessToken } = await res.json();
                return accessToken;
            }
            throw new Error('could not fetch token');
        }
        catch (e) {
            console.warn(e);
            throw e;
        }
    },
    getprofile: async (cookie) => {
        try {
            const res = await requests.get('/api/me', cookie);
            if (res.ok) {
                const user = await res.json();
                return user;
            }
            throw new Error('could not fetch user');
        }
        catch (e) {
            console.warn(e);
            throw e;
        }
        
    },
}