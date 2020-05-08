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

    list = flow(function* () {
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(r.SOURCES, token);
            return result;
        } catch (error) {
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);


    detail = flow(function* (element) {
        const id = element.id || element;
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(`${r.SOURCES}/${id}/stats`, token);
            return result;
        } catch (error) {
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);

    interval = flow(function* (element, intervalStart, intervalEnd) {
        const id = element.id || element;
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(`${r.SOURCES}/${id}/interval`, token, {
                start: intervalStart,
                end: intervalEnd,
            });
            return result;
        } catch (error) {
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);

    add = flow(function* (newSource) {
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.post(r.SOURCES, token, newSource);
            return result;
        } catch (error) {
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);

    delete = flow(function* (element) {
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.delete(r.SOURCES, token, element);
            return result;
        } catch (error) {
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
    }
}

export default SourcesStore;