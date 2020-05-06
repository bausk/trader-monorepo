import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
import useSWR, { cache } from 'swr';
import { observer } from 'mobx-react';
import Chart from "react-google-charts";
import { makeStyles } from "@material-ui/core/styles";
import Card from '@material-ui/core/Card';
import Container from '@material-ui/core/Container';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import Paper from "@material-ui/core/Paper";
import IconButton from "@material-ui/core/IconButton";
import ArrowBackIcon from "@material-ui/icons/ArrowBack";

const LightweightChart = dynamic(
    () => import('components/Graphics/LightweightChart'),
    { ssr: false }
  )
import { useStores } from 'components/rootStore';
import TableLayout from 'components/layouts/TableLayout';
import f from 'api/frontendRoutes';
import b from 'api/backendRoutes';


const dataHeader = [
    { type: 'string', id: 'IntervalName' },
    { type: 'date', id: 'Start' },
    { type: 'date', id: 'End' },
];

const useStyles = makeStyles(theme => ({
    container: {
        marginTop: theme.spacing(2),
        marginLeft: theme.spacing(0),
        marginRight: theme.spacing(0),
        padding: theme.spacing(1),
    },
}));

function ExploreSource() {
    const { sourcesStore } = useStores();
    const classes = useStyles();
    const router = useRouter();
    const [ startFetchDetail, setFetchDetail ] = useState();
    const cacheData = cache.get(b.SOURCES);
    const cachedDetail = cache.get(`${b.SOURCES}/${router.query.id}/stats`);
    const initialData = cacheData && cacheData.find(c => c.id === parseInt(router.query.id));
    const { data: detailData, mutate: mutateDetail, isValidating: isValidatingDetail } = useSWR(
        () => startFetchDetail ? `${b.SOURCES}/${router.query.id}/stats` : null,
        async (query) => {
            const r = await sourcesStore.detail(router.query.id);
            return r;
        },
        {
            revalidateOnFocus: false,
            revalidateOnReconnect: false,
        }
    );
    const { data: listData } = useSWR(
        () => !initialData ? `${b.SOURCES}` : null,
        async (query) => {
            const r = await sourcesStore.list();
            return r;
        },
        {
            revalidateOnFocus: false,
            revalidateOnReconnect: false,
        }
    );
    const info = listData?.find(c => c?.id === parseInt(router.query.id)) || initialData;
    console.log(info);
    const rows = detailData?.available_intervals?.map(i => ['Availability:', new Date(i[0]), new Date(i[1])])
        || cachedDetail?.available_intervals?.map(i => ['Availability:', new Date(i[0]), new Date(i[1])])
        || [];
    const chartData = [
        dataHeader,
        ...rows
    ];
    const getDetail = () => {
        if (startFetchDetail) {
            mutateDetail();
        }
        setFetchDetail(true);
    };

    return (
        <TableLayout
            title={info?.id}
            toolbar={() => (
                <IconButton
                    edge="start"
                    component="a"
                    onClick={() => router.push(f.EXPLORE)}
                    color="inherit"
                    aria-label="back to"
                >
                <ArrowBackIcon />
                </IconButton>
            )}
        >
            <Paper>
                <Container maxWidth="sm">
                    <Box py={4}>
                        <Typography variant="h4" component="h1" gutterBottom>
                            {info?.name}
                        </Typography>
                    </Box>
                </Container>
                <Container>
                    <Card className={classes.container}>
                        <Button onClick={getDetail} disabled={isValidatingDetail}>
                            Refresh Availability
                        </Button>
                        {isValidatingDetail && <LinearProgress />}
                        {Boolean(rows?.length) && (<Chart
                            chartType="Timeline"
                            height="150px"
                            data={chartData}
                            options={{
                                showRowNumber: true,
                            }}
                            rootProps={{ 'data-testid': '1' }}
                        />)}
                        <LightweightChart />
                    </Card>
                </Container>
            </Paper>
        </TableLayout>
    );
}

export default ExploreSource;
