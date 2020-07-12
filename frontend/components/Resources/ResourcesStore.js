import { observable, flow } from 'mobx';
import { fetchBackend, authenticatedFetchCreator } from 'api/fetcher';
import f from 'api/backendRoutes';


class ResourcesStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }

    resources = {
        listResource: flow(authenticatedFetchCreator(
            fetchBackend.get,
            f.RESOURCES
        )).bind(this),
        detailResource: flow(authenticatedFetchCreator(
            fetchBackend.get,
            f.RESOURCE_DETAIL
        )).bind(this),
        putResource: flow(authenticatedFetchCreator(
            fetchBackend.put,
            f.RESOURCE_DETAIL
        )).bind(this),
        changeResourceIsLive: flow(authenticatedFetchCreator(
            fetchBackend.put,
            f.RESOURCE_DETAIL,
            (data) => ({ live: !!data.live_session_id }),
        )).bind(this),
        patchResource: flow(authenticatedFetchCreator(
            fetchBackend.patch,
            f.RESOURCE_DETAIL,
        )).bind(this),
        addResource: flow(authenticatedFetchCreator(
            fetchBackend.post,
            f.RESOURCES,
        )).bind(this),
        deleteResource: flow(authenticatedFetchCreator(
            fetchBackend.delete,
            f.RESOURCES,
        )).bind(this),
    };

    hydrate = (data) => {
        Object.keys(data).forEach(k => this[k] = data[k]);
    }
}

export default ResourcesStore;