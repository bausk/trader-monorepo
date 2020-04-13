import { observable, flow} from 'mobx';
import { fetchBackend } from 'api/fetcher';
import r from 'api/backendRoutes';

class SourcesStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable sources;
    @observable state = "pending";

    listSourcesAsync = async () => {
        try {
            const token = this.rootStore.authStore.accessToken;
            console.log(token);
            debugger;
            const result = await fetchBackend.post(r.SOURCES, token);
            console.log(result);
            return result;
        } catch (error) {
            throw error;
        }
    }
    
    listSources = flow(function* () {
        this.sources = [];
        this.state = "pending";
        try {
            const token = this.rootStore.authStore.accessToken;
            const result = yield fetchBackend.post(r.SOURCES, token);
            this.state = "done";
            console.log(result);
            this.sources = result;
        } catch (error) {
            this.state = "error";
        }
    }).bind(this);

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
    }
}

export default SourcesStore;