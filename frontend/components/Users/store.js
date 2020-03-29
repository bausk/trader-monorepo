import { createContext } from 'react'
import { configure, observable, flow} from 'mobx';
import callApi from './api';
configure({ enforceActions: "observed" });


class Store {
    @observable users = "[]";
    @observable state = "pending";

    fetchProjects = flow(function* () {
        console.log(this);
        this.users = "[]";
        this.state = "pending";
        try {
            const users = yield callApi();
            const filteredUsers = users;
            this.state = "done";
            this.users = filteredUsers;
        } catch (error) {
            this.state = "error";
        }
    }).bind(this);
}

export default createContext(new Store());