import { observable, flow} from 'mobx';
import callApi from './UsersApi';


class UsersStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }
    @observable users = [];
    @observable state;

    fetchProjects = flow(function* () {
        this.users = [];
        this.state = "pending";
        try {
            const users = yield callApi();
            this.state = "done";
            this.users = users;
            this.rootStore.sourcesStore.sources = [];
        } catch (error) {
            this.state = "error";
        }
    }).bind(this);

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
    }

    getSources = () => {
        return this.rootStore.sourcesStore.sources;
    }
}

export default UsersStore;