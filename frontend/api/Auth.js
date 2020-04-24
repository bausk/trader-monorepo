import { fetchFrontend } from './fetcher';
import r from './frontendRoutes';

const Auth = {
    gettoken: async (cookie) => {
        try {
            const token = await fetchFrontend.get(r.GETTOKEN, cookie);
            if (!token) {
                throw new Error('could not fetch token');
            }
            return token;
        }
        catch (e) {
            throw new Error('could not fetch token');
        }
    },
    getTokenServerSide: async (req) => {
        const cookie = req && req.headers.cookie;
        if (cookie) {
            return await Auth.gettoken(cookie);
        }
    },
    getprofile: async (cookie) => {
        try {
            return await fetchFrontend.get(r.ME, cookie);
        }
        catch (e) {
            throw new Error('could not fetch user');
        }
    },
    checkLogin: async (req) => {
        const isServer = typeof window === 'undefined';
        if (isServer) {
            const cookie = req && req.headers.cookie;
            const user = await Auth.getprofile(cookie);
            if (!user) {
                throw new Error('user not available');
            }
            return user;
        } else {
            return undefined;
        }
    }
}

export default Auth;
