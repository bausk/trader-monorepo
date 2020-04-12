import { fetchFrontend } from './fetcher';
import r from './frontendRoutes';

const Auth = {
    gettoken: async () => {
        try {
            return await fetchFrontend.get(r.GETTOKEN);
        }
        catch (e) {
            throw new Error('could not fetch token');
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
}

export default Auth;
