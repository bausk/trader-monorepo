import React, { useMemo, useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { observer } from 'mobx-react';
import { useRouter } from 'next/router';
import Container from '@material-ui/core/Container';
import LinearProgress from '@material-ui/core/LinearProgress';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import { DateTime } from "luxon";

import { fetchStates } from 'components/constants';
import { useStores } from 'components/rootStore';
import useManualSWR from 'components/Hooks/useManualSWR';
import b from 'api/backendRoutes';


const LightweightChart = dynamic(
    () => import('components/Graphics/LightweightChart'),
    { ssr: false }
);

function SessionChart({ session }) {
    const router = useRouter();
    const [ show, setShow ] = useState(false);
    const { sessionStore } = useStores();
    console.log(DateTime.local().toISO());
    console.log(DateTime.utc().toISO());
    useEffect(() => {
        console.log('Running effect...');
        const params = {
            period: 5,
            from_datetime: DateTime.utc().minus({hours: 6}).toISO(),
            label: 'btcusd',
            data_type: 1
        }
        sessionStore.getData(session.id, params);
    }, []);
    const isButtonEnabled = sessionStore.state === fetchStates.SUCCESS;
    const isLoading = sessionStore.state === fetchStates.FETCHING;
    const onVisibleTimeRangeChanged = useCallback(() => {
        console.log('time range changed');
    }, []);
    const onClick = useCallback(() => {
        setShow(true);
    }, []);
    return (
        <>
        <Container>
            <Box>
                {!show && (
                <Button onClick={onClick} disabled={!isButtonEnabled}>
                    Show Chart
                </Button>
                )}
                {isLoading && <LinearProgress />}
            </Box>
            {show && 
                <LightweightChart
                    dataType="candlestick"
                    data={sessionStore.ohlc}
                    onVisibleTimeRangeChanged={onVisibleTimeRangeChanged}
                />
            }
        </Container>
        </>
    );
}

export default observer(SessionChart);