import { observable, flow, action } from 'mobx';
import { observer } from 'mobx-react';
import { fetchBackend, authenticatedFetchCreator } from 'api/fetcher';
import b from 'api/backendRoutes';
import { fetchStates } from 'components/constants';


class SessionStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable ohlc;
    @observable state = fetchStates.IDLE;

    getData = flow(function* (element, params) {
        this.state = fetchStates.FETCHING;
        const id = element.id || element;
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.get(b.SESSIONS_DATA(id), token, params);
            this.ohlc = result;
            this.state = fetchStates.SUCCESS;
        } catch (error) {
            this.state = fetchStates.ERROR;
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