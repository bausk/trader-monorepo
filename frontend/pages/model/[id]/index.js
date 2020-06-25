import React from 'react';
import { useRouter } from 'next/router';
import useSWR, { cache } from 'swr';
import { observer } from 'mobx-react';
import { makeStyles } from "@material-ui/core/styles";
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import IconButton from "@material-ui/core/IconButton";
import ArrowBackIcon from "@material-ui/icons/ArrowBack";
import { useStores } from 'components/rootStore';
import IntervalChart from 'components/Graphics/IntervalChart';
import Properties from 'components/Blocks/Properties';
import ModelProperties from 'components/Blocks/ModelProperties';
import TableLayout from 'components/layouts/TableLayout';
import f from 'api/frontendRoutes';
import b from 'api/backendRoutes';

const useStyles = makeStyles(theme => ({
    container: {
        marginTop: theme.spacing(2),
        marginLeft: theme.spacing(0),
        marginRight: theme.spacing(0),
        padding: theme.spacing(1),
    },
    title: {
        paddingLeft: theme.spacing(3)
    },
    paper: {
        padding: theme.spacing(2),
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
        height: 140,
    },
    chart: {
        padding: theme.spacing(2),
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
    },
}));

function ModelDetailView() {
    const { sourcesStore } = useStores();
    const classes = useStyles();
    const router = useRouter();
    const cacheData = cache.get(b.STRATEGIES);
    const initialData = cacheData && cacheData.find(c => c.id === parseInt(router.query.id));
    const { data: listData } = useSWR(
        () => !initialData ? `${b.STRATEGIES}` : null,
        async (query) => {
            const r = await sourcesStore.strategies.list();
            return r;
        },
        {
            revalidateOnFocus: false,
            revalidateOnReconnect: false,
        }
    );
    console.log(listData);
    const model = listData?.find(c => c?.id === parseInt(router.query.id)) || initialData;

    return (
        <TableLayout
            toolbar={() => (
                <>
                    <IconButton
                        edge="start"
                        component="a"
                        onClick={() => router.push(f.MODEL)}
                        color="inherit"
                        aria-label="back to"
                    >
                    <ArrowBackIcon />
                    </IconButton>
                    <Typography component="h1" variant="h4" color="inherit" noWrap className={classes.title}>
                        Model: {model?.name}
                    </Typography>
                </>
            )}
        >
            <Container maxWidth="lg" className={classes.container}>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Paper className={classes.paper}>
                            <ModelProperties model={model} />
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Paper className={classes.paper}>
                            <Properties session={model?.live_session_model} />
                        </Paper>
                    </Grid>
                    <Grid item xs={12}>
                        <Paper className={classes.chart}>
                            <IntervalChart />
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </TableLayout>
    );
}

export default observer(ModelDetailView);
