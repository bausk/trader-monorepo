import { SAVE_DATA } from './FetchData.actions';
import update from 'immutability-helper';

const exampleInitialState = {
    data: {},
    normalizedData: [],
    header: [],
    retrievedAt: null
}


// REDUCERS
export default (state = exampleInitialState, action) => {
    switch (action.type) {
        case SAVE_DATA.type: {
            const columns = Object.keys(action.data);
            const header = columns;
            const normalizedData = Object.keys(action.data.DateTime).map((key) => {
                const row = columns.reduce((acc, col) => {
                    acc[col] = action.data[col][key];
                    return acc
                }, {});
                return row;
            });
            return update(state, {
                data: {
                    $set: action.data
                },
                normalizedData: {
                    $set: normalizedData
                },
                header: {
                    $set: header
                },
                retrievedAt: {
                    $set: new Date()
                }
            });
        }
        default:
            return state;
    }
};