import { LOGIN_USER, FORGET_USER } from './Login.actions';
import update from 'immutability-helper';

const exampleInitialState = {
    user: null
};

// REDUCERS
export default (state = exampleInitialState, action) => {
    switch (action.type) {
        case LOGIN_USER.type: {
            return update(state, {
                user: {
                    $set: action.user
                }
            });
        }
        case FORGET_USER.type: {
            return exampleInitialState;
        }        
        default:
            return state;
    }
};