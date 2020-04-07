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
                    cookie: auth.cookie,
                },
              }
            : (auth.token ? {
                Authorization: `Bearer ${auth.token}`
            } : {}))
        }
    );
};

const requests = {
    del: async (url, cookie = '') => await request('DELETE', isServer ? `${API_ROOT}${url}` : url, { cookie }),
    get: async (url, cookie = '') => await request('GET', isServer ? `${API_ROOT}${url}` : url, { cookie }),
    put: async (url, cookie = '') => await request('PUT', isServer ? `${API_ROOT}${url}` : url, { cookie }),
    post: async (url, cookie = '') => await request('POST', isServer ? `${API_ROOT}${url}` : url, { cookie }),
  };

const service = {
    del: async (url, token) => await request('DELETE', `${SERVICE_ROOT}${url}`, { token }),
    get: async (url, token) => await request('GET', `${SERVICE_ROOT}${url}`,{ token }),
    put: async (url, token) => await request('PUT', `${SERVICE_ROOT}${url}`,{ token }),
    post: async (url, token) => await request('POST', `${SERVICE_ROOT}${url}`, { token }),
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