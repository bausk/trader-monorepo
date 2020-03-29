import React from 'react';
import PropTypes from 'prop-types';
import { useFetchUser } from '../lib/user'

const useLoading = () => {
    const [ loading, setState ] = React.useState({});
    const setLoading = React.useCallback((key, state) => {
        setState({
            ...loading,
            [key]: state
        });
    }, [])
    return { loading, setLoading };
}

export const LoadingContext = React.createContext({ loading: {}, setLoading: () => { } });


export function LoadingProvider({ children }) {
    const loading = useLoading();
    return (
      <LoadingContext.Provider value={loading}>
        {children}
      </LoadingContext.Provider>
    );
  }