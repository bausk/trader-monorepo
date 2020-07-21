import { observable, flow, action } from 'mobx';
import { observer } from 'mobx-react';
import { fetchBackend, authenticatedFetchCreator } from 'api/fetcher';
import b from 'api/backendRoutes';
import { fetchStates } from 'components/constants';


const merge = (oldData, newData, key='time') => {
    const newIndexes = new Set(newData.map(el => el[key]));
    const oldUniques = oldData.filter(el => !newIndexes.has(el[key]));
    const merged = oldUniques.concat(newData);
    return merged.sort((a, b) => (a[key] > b[key]) ? 1 : -1);
}

class SessionStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable newOhlc = [];
    @observable newAutorefreshOhlc = [];
    @observable markers = [];
    @observable state = fetchStates.IDLE;
    @observable period = 5;

    getMarkers = flow(function* (element, params) {
        const id = element?.id || element;
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(b.SESSION_MARKERS(id), token, params);
            this.markers = result.reduce((obj, marker) => {
                const key = Date.parse(marker.timestamp) / 1000;
                marker.primitives = JSON.parse(marker.primitives);
                obj[key] = marker;
                return obj;
            }, {});
        } catch (error) {
            this.state = fetchStates.ERROR;
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);

    getData = flow(function* (element, params) {
        this.state = fetchStates.FETCHING;
        const id = element?.id || element;
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(b.SESSIONS_DATA(id), token, params);
            this.newOhlc = result;
            this.state = fetchStates.SUCCESS;
        } catch (error) {
            this.state = fetchStates.ERROR;
            if (error.message === '401') {
                yield this.rootStore.authStore.relogin();
            }
        }
    }).bind(this);

    getAutorefreshData = flow(function* (element, params) {
        const id = element?.id || element;
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(b.SESSIONS_DATA(id), token, params);
            this.newAutorefreshOhlc = result;
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

export default SessionStore;