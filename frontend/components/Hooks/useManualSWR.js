import React, { useState, useCallback, useEffect } from 'react';
import useSWR, { cache } from 'swr';

const useManualSWR = (cacheKey, fetchKey, fetcher, options) => {
    const [ startFetch, setFetch ] = useState(false);
    const cachedData = cache.get(cacheKey);
    const { data: fetchData, mutate, isValidating } = useSWR(
        () => startFetch ? fetchKey : null,
        fetcher,
        {
            ...options,
            revalidateOnFocus: false,
            revalidateOnReconnect: false,
        }
    );
    useEffect(() => {
        if(!isValidating) {
            setFetch(false);
        }
    }, [isValidating]);
    const onFetch = useCallback(() => {
        if (startFetch) {
            mutate();
        }
        setFetch(true);
    }, [startFetch]);
    const data = fetchData || cachedData;
    return { onFetch, data, isValidating };
}

export default useManualSWR;
