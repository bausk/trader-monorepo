import { observable, flow, action } from 'mobx';
import { observer } from 'mobx-react';
import { fetchBackend } from 'api/fetcher';
import r from 'api/backendRoutes';

class SourcesStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable sources;
    @observable state = "pending";

    listAsync = async () => {
        try {
            const token = this.rootStore.authStore.accessToken;
            console.log(token);
            debugger;
            const result = await fetchBackend.get(r.SOURCES, token);
            console.log(result);
            return result;
        } catch (error) {
            throw error;
        }
    }
    
    list = flow(function* () {
        this.sources = [];
        this.state = "pending";
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(r.SOURCES, token);
            this.state = "done";
            console.log(result);
            this.sources = result;
            return result;
        } catch (error) {
            this.state = "error";
            if (error.message === '401') {
                yield this.rootStore.authStore.logout();
            }
        }
    }).bind(this);

    add = flow(function* () {
        this.state = "pending";
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.post(r.SOURCES, token, { type: 'fromfrontie' });
            this.state = "done";
            return result;
        } catch (error) {
            this.state = "error";
            if (error.message === '401') {
                yield this.rootStore.authStore.logout();
            }
        }
    }).bind(this);

    delete = flow(function* (element) {
        this.state = "pending";
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.delete(r.SOURCES, token, element);
            this.state = "done";
            return result;
        } catch (error) {
            this.state = "error";
            if (error.message === '401') {
                yield this.rootStore.authStore.logout();
            }
        }
    }).bind(this);

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
    }
}

export default SourcesStore;