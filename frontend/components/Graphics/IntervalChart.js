import React, { useMemo, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { observer } from 'mobx-react';
import { useRouter } from 'next/router';
import Container from '@material-ui/core/Container';
import LinearProgress from '@material-ui/core/LinearProgress';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import {
    MuiPickersUtilsProvider,
    DatePicker
} from '@material-ui/pickers';
import LuxonUtils from '@date-io/luxon';

import { useStores } from 'components/rootStore';
import useManualSWR from 'components/Hooks/useManualSWR';
import b from 'api/backendRoutes';


const LightweightChart = dynamic(
    () => import('components/Graphics/LightweightChart'),
    { ssr: false }
);
const luxon = new LuxonUtils();

function IntervalChart() {
    const router = useRouter();
    const { sourcesStore } = useStores();
    const [ start, setStart ] = useState(luxon.date());
    const [ end, setEnd ] = useState(luxon.date());
    const { onFetch, data, isValidating } = useManualSWR(
        [`${b.SOURCES}/${router.query.id}/interval`, start, end],
        [`${b.SOURCES}/${router.query.id}/interval`, start, end],
        async (query, start, end) => {
            const r = await sourcesStore.interval(
                router.query.id,
                start.toISO(),
                end.toISO(),
            );
            return r.data;
        }
    );
    return (
        <MuiPickersUtilsProvider utils={LuxonUtils}>
            <Container>
                <Box>
                    <DatePicker
                        value={start}
                        onChange={setStart}
                        autoOk
                        label="Start"
                        disableFuture
                    />
                    <DatePicker
                        value={end}
                        onChange={setEnd}
                        autoOk
                        label="End"
                        disableFuture
                    />
                    {isValidating && <LinearProgress />}
                </Box>
                <Box>
                    <Button onClick={onFetch} disabled={isValidating}>
                        Refresh Availability
                    </Button>
                    {isValidating && <LinearProgress />}
                </Box>
                <LightweightChart
                    data={data}
                    mapper={() => {}}
                />
            </Container>
        </MuiPickersUtilsProvider>
    );
}

export default observer(IntervalChart);