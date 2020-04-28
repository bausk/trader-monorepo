import React from 'react';
import { useRouter } from 'next/router';
import Card from '@material-ui/core/Card';
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";

import Paper from "@material-ui/core/Paper";
import IconButton from "@material-ui/core/IconButton";
import ArrowBackIcon from "@material-ui/icons/ArrowBack";
import { useTheme } from '@material-ui/core/styles';
import { observer } from 'mobx-react';
import TableLayout from 'components/layouts/TableLayout';
import Chart from "react-google-charts";
import f from 'api/frontendRoutes';


const data = [
    [
        { type: 'string', id: 'President' },
        { type: 'date', id: 'Start' },
        { type: 'date', id: 'End' },
    ],
    [ 'Washington', new Date(2018, 8, 30), new Date(2018, 12, 4) ],
    [ 'Washington', new Date(2019, 2, 4),  new Date(2019, 4, 4) ]
];

function ExploreSource({ sources }) {
    const { sourcesStore, authStore } = useStores();
    const router = useRouter();
    const { data, error, mutate } = useSWR(
      [`${r.SOURCES}/${router.query.id}`, authStore.accessToken],
      async (query, token) => {
        return await fetchBackend.get(query, token);
      }
    );
    if(error) {
      authStore.login();
    }
    
    return (
        <TableLayout
            title="Source"
            toolbar={() => (
                <IconButton
                edge="start"
                component="a"
                href={f.EXPLORE}
                color="inherit"
                aria-label="back to"
                >
                <ArrowBackIcon />
                </IconButton>
            )}
        >
            <Paper>
                <Card>
                    <Chart
                        chartType="Timeline"
                        height="600px"
                        data={data}
                        options={{
                            showRowNumber: true,
                        }}
                        rootProps={{ 'data-testid': '1' }}
                    />
                </Card>
            </Paper>
        </TableLayout>
    );
}

export default observer(ExploreSource);
