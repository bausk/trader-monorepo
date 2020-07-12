import React from 'react';
import { useStaticRendering } from 'mobx-react'

import ResourcesStore from './Resources/ResourcesStore';
import SourcesStore from './Sources/SourcesStore';
import SessionStore from './Sessions/SessionStore';
import AuthStore from './Auth/AuthStore';


const isServer = typeof window === 'undefined'
// eslint-disable-next-line react-hooks/rules-of-hooks
useStaticRendering(isServer)

export class RootStore {
    constructor(initialState) {
        this.authStore = new AuthStore(this);
        this.sourcesStore = new SourcesStore(this);
        this.resourcesStore = new ResourcesStore(this);
        this.sessionStore = new SessionStore(this);
        this.hydrate(initialState);
    }
    hydrate = ({ authStore, sourcesStore, resourcesStore, sessionStore }) => {
        authStore && this.authStore.hydrate(authStore);
        sourcesStore && this.sourcesStore.hydrate(sourcesStore);
        resourcesStore && this.resourcesStore.hydrate(resourcesStore);
        sessionStore && this.sessionStore.hydrate(sessionStore);
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
