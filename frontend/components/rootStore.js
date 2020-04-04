import { createContext } from 'react'
import { action, observable } from 'mobx'
import { useStaticRendering } from 'mobx-react'
const isServer = typeof window === 'undefined'
// eslint-disable-next-line react-hooks/rules-of-hooks
useStaticRendering(isServer)

export class UserStore {
    constructor(rootStore) {
        this.rootStore = rootStore
    }

    getTodos() {
        // access todoStore through the root store
        return this.rootStore.todoStore.todos.concat(['user-added todo!']);
    }
    
    @action addTodos = () => {
        this.rootStore.todoStore.todos = this.rootStore.todoStore.todos.concat(['action-added todo!']);
    }
    hydrate = (users) => {
    }
}

export class TodoStore {
    constructor(rootStore) {
        this.rootStore = rootStore
    }
    @observable todos = []
    hydrate = (todos) => {
        this.todos = todos;
    }
}

export class RootStore {
    constructor() {
        this.userStore = new UserStore(this);
        this.todoStore = new TodoStore(this);
    }
    hydrate = ({ todos, users }) => {
        console.log('hydrating!');
        this.userStore.hydrate(users);
        this.todoStore.hydrate(todos);
    }
}

export const rootStoreContext = React.createContext();

export const StoreProvider = ({ store, children }) => {
    return <rootStoreContext.Provider value={store}>{children}</rootStoreContext.Provider>;
};

export const useStores = (which) => {
    const _store = React.useContext(rootStoreContext);
    if (!_store) {
        throw new Error('StoreProvider should be added at top-level components');
    }
    if (which) {
        return _store[which];
    }
    return _store;
};
