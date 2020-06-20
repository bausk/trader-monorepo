import React from 'react';
import { useStaticRendering } from 'mobx-react'

import SourcesStore from './Sources/SourcesStore';
import AuthStore from './Auth/AuthStore';


const isServer = typeof window === 'undefined'
// eslint-disable-next-line react-hooks/rules-of-hooks
useStaticRendering(isServer)

export class RootStore {
    constructor(initialState) {
        this.authStore = new AuthStore(this);
        this.sourcesStore = new SourcesStore(this);
        this.hydrate(initialState);
    }
    hydrate = ({ authStore, sourcesStore }) => {
        authStore && this.authStore.hydrate(authStore);
        sourcesStore && this.sourcesStore.hydrate(sourcesStore);
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
