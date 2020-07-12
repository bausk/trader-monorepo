import React, { useRef, useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { observer } from 'mobx-react';
import Container from '@material-ui/core/Container';
import LinearProgress from '@material-ui/core/LinearProgress';
import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import { DateTime } from "luxon";

import { fetchStates } from 'components/constants';
import { useStores } from 'components/rootStore';


const LightweightChart = dynamic(
    () => import('components/Graphics/LightweightChart'),
    { ssr: false }
);

function useInterval(callback, delay) {
    const savedCallback = useRef();

    // Remember the latest callback.
    useEffect(() => {
        savedCallback.current = callback;
    }, [callback]);

    // Set up the interval.
    useEffect(() => {
        function tick() {
            savedCallback.current();
        }
        if (delay !== null) {
            let id = setInterval(tick, delay);
            return () => clearInterval(id);
        }
    }, [delay]);
}

const useStyles = makeStyles({
    container: {
        height: 0,
    },
    hover: {
        position: 'relative',
        zIndex: 10,
    },
});

const HoverLinearProgress = () => {
    const classes = useStyles();
    return (
        <div className={classes.container} >
            <LinearProgress className={classes.hover} />
        </div>
    );
}


function SessionChart({ session }) {
    const [ show, setShow ] = useState(false);
    const { sessionStore } = useStores();
    const period = sessionStore.period;
    useEffect(() => {
        console.log('Running effect...');
        const params = {
            period: period,
            from_datetime: DateTime.utc().minus({hours: 3}).toISO(),
            label: 'btcusd',
            data_type: 1
        }
        sessionStore.getData(session, params);
    }, []);
    const isButtonEnabled = sessionStore.state === fetchStates.SUCCESS;
    const isAutorefreshEnabled = sessionStore.state !== fetchStates.IDLE;
    const isLoading = sessionStore.state === fetchStates.FETCHING;
    console.log(sessionStore.state);
    const onRangeChanged = (a) => {
        if (a?.from && a?.to) {
            const params = {
                period: period,
                from_datetime: a.from.toISO(),
                to_datetime: a.to.toISO(),
                label: 'btcusd',
                data_type: 1
            }
            sessionStore.getData(session, params);
        }
    };
    const onClick = useCallback(() => {
        setShow(true);
    }, []);

    useInterval(() => {
        const now = DateTime.utc();
        const params = {
            period: period,
            from_datetime: now.minus({minutes: 30}).toISO(),
            to_datetime: now.plus({minutes: 5}).toISO(),
            label: 'btcusd',
            data_type: 1
        }
        sessionStore.getAutorefreshData(session, params);
    }, isAutorefreshEnabled ? 4000 : null)

    return (
        <>
        <Container>
            <Box>
                {!show && (
                <Button onClick={onClick} disabled={!isButtonEnabled}>
                    Show Chart
                </Button>
                )}
                {isLoading && <HoverLinearProgress />}
            </Box>
            {show && 
                <LightweightChart
                    dataType="candlestick"
                    newData={sessionStore.newOhlc}
                    newAutorefreshData={sessionStore.newAutorefreshOhlc}
                    onRangeChanged={onRangeChanged}
                    period={period}
                />
            }
        </Container>
        </>
    );
}

export default observer(SessionChart);