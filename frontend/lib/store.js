import { createStore, combineReducers, applyMiddleware } from 'redux';
import { composeWithDevTools } from 'redux-devtools-extension';
import thunkMiddleware from 'redux-thunk';
import table from '../components/FetchData/FetchData.reducers';
import fetchMiddleware from '../components/FetchData/FetchData.middleware';
import user from '../components/Login/Login.reducers';
import loginMiddleware from '../components/Login/Login.middleware';


const rootReducer = (state, action) => {
    const intermediateState = combineReducers({
        table,
        user
    })(state, action);
    return intermediateState;
};

export const initializeStore = (initialState = {}) => {
  return createStore(
    rootReducer,
    initialState,
    composeWithDevTools(applyMiddleware(
        thunkMiddleware,
        fetchMiddleware,
        loginMiddleware
        ))
  )
};
