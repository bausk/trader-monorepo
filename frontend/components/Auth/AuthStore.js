import { observable, flow, action } from 'mobx';
import Router from 'next/router';
import routes from 'api/frontendRoutes';
import Auth from 'api/Auth';


class AuthStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable user;
    @observable accessToken;
    @observable lastUpdate;
    @observable loading = 'pending';
    @action start = () => {
        this.timer = setInterval(flow(function* () {
            this.lastUpdate = Date.now();
            if (this.user) {
                try {
                    const token = yield Auth.gettoken();
                    this.accessToken = token.accessToken;
                } catch (e) {
                    // TODO: nullify accessToken?
                    this.stop();
                }
            } else {
                this.stop();
            }
        }.bind(this)), 180000)
    };
    
    stop = () => clearInterval(this.timer);

    getUser = flow(function* (cookie) {
        this.loading = 'fetching';
        let user;
        try {
            user = yield Auth.getprofile(cookie);
            this.user = user;
            this.loading = 'done';
            this.start();
        } catch (e) {
            return this.logout('foreign source');
        }
    });

    @action login = () => {
        this.loading = 'fetching';
        Router.push(routes.LOGIN);
    };

    @action relogin = () => {
        this.loading = 'fetching';
        this.user = null;
        localStorage.setItem('logout', new Date())
        Router.push(routes.LOGIN);
    };

    @action logout = (foreignSource = false) => {
        this.loading = 'fetching';
        this.user = null;
        if (!foreignSource) {
            localStorage.setItem('logout', new Date())
        }
        Router.push(routes.LOGOUT);
    };

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
        if (data?.user && typeof window !== 'undefined') {
            localStorage.setItem('login', new Date())
        }
    };
}

export default AuthStore;