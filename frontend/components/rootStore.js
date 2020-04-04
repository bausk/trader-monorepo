import React from 'react';
import { action, observable } from 'mobx'
import { useStaticRendering } from 'mobx-react'

import SourcesStore from './Sources/SourcesStore';
import UsersStore from './Users/UsersStore';


const isServer = typeof window === 'undefined'
// eslint-disable-next-line react-hooks/rules-of-hooks
useStaticRendering(isServer)

export class RootStore {
    constructor() {
        this.usersStore = new UsersStore(this);
        this.sourcesStore = new SourcesStore(this);
    }
    hydrate = ({ usersStore, sourcesStore }) => {
        this.usersStore.hydrate(usersStore);
        this.sourcesStore.hydrate(sourcesStore);
    }
}

export const rootStoreContext = React.createContext();

export const StoreProvider = ({ store, children }) => {
    return <rootStoreContext.Provider value={store}>{children}</rootStoreContext.Provider>;
};

export const useStores = () => {
    const _store = React.useContext(rootStoreContext);
    if (!_store) {
        throw new Error('StoreProvider should be added at top-level components');
    }
    return _store;
};
