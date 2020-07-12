import React, { useCallback } from 'react';
import useSWR from 'swr';
import { useRouter } from 'next/router';
import TableContainer from "@material-ui/core/TableContainer";
import Paper from "@material-ui/core/Paper";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import AddIcon from "@material-ui/icons/Add";
import RefreshIcon from "@material-ui/icons/Refresh";
import { observer } from 'mobx-react';
import TableLayout from 'components/layouts/TableLayout';
import CreateEditEntityModal from 'components/Modals/CreateEditEntityModal';
import { useStores } from 'components/rootStore';
import { DeleteButton } from 'components/buttons';
import b from 'api/backendRoutes';
import f from 'api/frontendRoutes';


function ResourceList() {
  const { resourcesStore, sourcesStore, authStore } = useStores();
  const router = useRouter();
  const { data, error, mutate } = useSWR(
    b.RESOURCES,
    resourcesStore.resources.listResource
  );

  const { data: sourcesList } = useSWR(
    b.SOURCES,
    sourcesStore.list
  );

  const newModal = router.asPath === f.RESOURCE_NEW;

  const onAdd = useCallback(async () => {
    return router.push(f.EXPLORE, f.RESOURCE_NEW);
  }, [router]);

  const onSubmit = useCallback(async (result) => {
    const newResource = {
      id: undefined,
      ...result
    };
    mutate(async (prev) => [...prev, newResource], false);
    mutate(resourcesStore.resources.addResource(newResource));
  }, []);

  const onClose = useCallback(() => {
    return router.push(f.EXPLORE);
  }, [router]);

  const onRefresh = useCallback(async () => {
    mutate();
  }, [mutate]);
  const { user, loading } = authStore;
  const rows = data || [];
  if (!loading && !user) {
    return null;
  }
  
  return (
    <TableLayout
      title="Source Assemblies"
      toolbar={() => (
        <>
          <CreateEditEntityModal
            open={newModal}
            onClose={onClose}
            onSubmit={onSubmit}
            sources={sourcesList}
          />
          <IconButton
            edge="start"
            onClick={onAdd}
            color="inherit"
            aria-label="menu"
          >
            <AddIcon />
          </IconButton>
          <IconButton
            onClick={onRefresh}
            color="inherit"
            aria-label="menu"
          >
            <RefreshIcon />
          </IconButton>
        </>
      )}
    >
      <TableContainer component={Paper}>
      <Table aria-label="simple table">
      <TableHead>
        <TableRow>
          <TableCell>Resource ID</TableCell>
          <TableCell>Name</TableCell>
          <TableCell>Live Sources</TableCell>
          <TableCell>Backtest Sources</TableCell>
          <TableCell align="right">Operations</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((row, i) => {
          const primaryLive = row.primary_live_source_model && `${row.primary_live_source_model.id}(${row.primary_live_source_model.name})`;
          const secondaryLive = row.secondary_live_source_model && `${row.secondary_live_source_model.id}(${row.secondary_live_source_model.name})`;
          const primaryBacktest = row.primary_backtest_source_model && `${row.primary_backtest_source_model.id}(${row.primary_backtest_source_model.name})`;
          const secondaryBacktest = row.secondary_backtest_source_model && `${row.secondary_backtest_source_model.id}(${row.secondary_backtest_source_model.name})`;
          const liveRepresentation = [ primaryLive, secondaryLive ].filter(Boolean).join(' + ')
          const backtestRepresentation = [ primaryBacktest, secondaryBacktest ].filter(Boolean).join(' + ')
          return (
            <TableRow key={i}>
              <TableCell component="th" scope="row">
                <b>
                  {row.id}
                </b>
              </TableCell>
              <TableCell>
                {row.name}
              </TableCell>
              <TableCell>
                {liveRepresentation}
              </TableCell>
              <TableCell>
                {backtestRepresentation}
              </TableCell>
              <TableCell align="right">
                <DeleteButton element={row} mutate={mutate} onDelete={resourcesStore.resources.deleteResource} />
              </TableCell>
            </TableRow>
          ); 
        })}
      </TableBody>
  </Table>
  </TableContainer>
  </TableLayout>
  )
}

export default observer(ResourceList);
