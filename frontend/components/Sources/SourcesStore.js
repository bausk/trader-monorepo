import { observable, flow, action } from 'mobx';
import { observer } from 'mobx-react';
import { fetchBackend, authenticatedFetchCreator } from 'api/fetcher';
import f from 'api/backendRoutes';


class SourcesStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }

    strategies = {
        list: flow(authenticatedFetchCreator(
            fetchBackend.get,
            f.STRATEGIES
        )).bind(this),
        detail: flow(authenticatedFetchCreator(
            fetchBackend.get,
            (id) => `${f.STRATEGIES}/${id}`,
        )).bind(this),
        put: flow(authenticatedFetchCreator(
            fetchBackend.put,
            (data) => `${f.STRATEGIES}/${data.id}`
        )).bind(this),
        putIsLive: flow(authenticatedFetchCreator(
            fetchBackend.put,
            (data) => `${f.STRATEGIES}/${data.id}/live`,
            (data) => ({ live: !!data.live_session_id }),
        )).bind(this),
        patch: flow(authenticatedFetchCreator(
            fetchBackend.patch,
            (id) => `${f.STRATEGIES}/${id}`,
        )).bind(this),
        add: flow(authenticatedFetchCreator(
            fetchBackend.post,
            f.STRATEGIES,
        )).bind(this),
        delete: flow(authenticatedFetchCreator(
            fetchBackend.delete,
            f.STRATEGIES,
        )).bind(this),
    };

    list = flow(function* () {
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(f.SOURCES, token);
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
            const result = yield fetchBackend.get(`${f.SOURCES}/${id}/stats`, token);
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
            const result = yield fetchBackend.get(`${f.SOURCES}/${id}/interval`, token, {
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
            const result = yield fetchBackend.post(f.SOURCES, token, newSource);
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
            const result = yield fetchBackend.delete(f.SOURCES, token, element);
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