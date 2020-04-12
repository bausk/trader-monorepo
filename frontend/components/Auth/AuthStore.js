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
            console.log(`trying to get access token... ${this.user ? 'proceeding': 'no user'}`);
            if (this.user) {
                try {
                    const token = yield Auth.gettoken();
                    this.accessToken = token;
                } catch (e) {
                    this.stop();
                }
            } else {
                this.stop();
            }
        }.bind(this)), 6000)
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
        if (data.user) {
            localStorage.setItem('login', new Date())
        }
    };
}

export default AuthStore;