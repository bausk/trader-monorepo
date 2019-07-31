import axios from 'axios';
import { FETCH, SAVE_DATA } from './FetchData.actions';

const API_URL = process.env.API_URL;

export default store => next => (action) => {
    const { type } = action;
    const state = store.getState();
    switch (type) {
        case FETCH.type: {
            const { retrievedAt } = state.table;
            if (retrievedAt !== null) {
                return next(action);
            }
            
            
            const headers = { 'Authorization': `Bearer token` }
            axios.get(`${API_URL}/private`, { headers })
                .then((response) => {
                    store.dispatch(SAVE_DATA.action(response.data));
                })
                .catch((error) => {
                });
            break;
        }
        default: {
            return next(action);
        }
    }
};
