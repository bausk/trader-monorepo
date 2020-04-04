import { observable, flow} from 'mobx';
import callApi from './SourcesApi';


class SourcesStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable sources;
    @observable state = "pending";

    fetchProjects = flow(function* () {
        this.sources = [];
        this.state = "pending";
        try {
            const result = yield callApi();
            this.state = "done";
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