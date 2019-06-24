import { createStore, combineReducers, applyMiddleware } from 'redux';
import { composeWithDevTools } from 'redux-devtools-extension';
import thunkMiddleware from 'redux-thunk';
import table from '../components/FetchData/FetchData.reducers';
import fetchMiddleware from '../components/FetchData/FetchData.middleware';


const rootReducer = (state, action) => {
    const intermediateState = combineReducers({
        table
    })(state, action);
    return intermediateState;
};

export const initializeStore = (initialState = {}) => {
  return createStore(
    rootReducer,
    initialState,
    composeWithDevTools(applyMiddleware(
        thunkMiddleware,
        fetchMiddleware
        ))
  )
};
