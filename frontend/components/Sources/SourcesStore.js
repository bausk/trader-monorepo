import { createContext } from 'react'
import { configure, observable, flow} from 'mobx';
import callApi from './api';
configure({ enforceActions: "observed" });


class Store {
    @observable sources;
    @observable state = "pending";

    fetchProjects = flow(function* () {
        this.users = [];
        this.state = "pending";
        try {
            const result = yield callApi();
            this.state = "done";
            this.sources = result;
        } catch (error) {
            this.state = "error";
        }
    }).bind(this);
}

export default Store;