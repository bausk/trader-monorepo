import { observable, flow, action } from 'mobx';
import { Auth } from '../apiCall';

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
            this.lastUpdate = Date.now()
            console.log(`trying to get access token... ${this.user ? 'proceeding': 'no user'}`);
            if (this.user) {
                const token = yield Auth.gettoken();
                this.accessToken = token;
            }
        }.bind(this)), 6000)
    };
    
    stop = () => clearInterval(this.timer);

    getUser = flow(function* (cookie) {
        this.loading = 'fetching';
        const user = yield Auth.getprofile(cookie);
        this.user = user;
        this.loading = 'done';
    });

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
    };
}

export default AuthStore;