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
import NewStrategyModal from 'components/Modals/NewStrategyModal';
import { useStores } from 'components/rootStore';
import { DeleteButton } from 'components/buttons';
import b from 'api/backendRoutes';
import f from 'api/frontendRoutes';

function ListStrategies() {
  const { sourcesStore, authStore } = useStores();
  const router = useRouter();
  const { data, error, mutate } = useSWR(
    b.STRATEGIES,
    async () => {
      return await sourcesStore.strategies.list();
    }
  );
  const newModal = router.asPath === f.MODEL_NEW;
  const onAdd = useCallback(async () => {
    return router.push(f.MODEL, f.MODEL_NEW);
  }, [router]);
  const onSubmit = useCallback(async (result) => {
    const newStrategy = {
      id: undefined,
      name: result.name,
      typename: result.typename,
      config_json: JSON.stringify({
      }),
    }
    mutate(async (prev) => [...prev, newStrategy], false);
    mutate(sourcesStore.strategies.add(newStrategy));
  }, []);
  const onClose = useCallback(() => {
    return router.push(f.MODEL);
  }, [router]);

  const onRefresh = useCallback(async () => {
    mutate();
  }, []);
  const { user, loading } = authStore;
  console.log(router);
  const rows = data || [];
  if (!loading && !user) {
    return null;
  }
  
  return (
    <TableLayout
      title="Strategies"
      toolbar={() => (
        <>
          <NewStrategyModal
            open={newModal}
            onClose={onClose}
            onSubmit={onSubmit}
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
          <TableCell>Strategy ID</TableCell>
          <TableCell>Type</TableCell>
          <TableCell align="right">Operations</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((row, i) => (
          <TableRow key={i}>
            <TableCell component="th" scope="row">
              <Button
                onClick={() => router.push(`${f.MODEL}/[id]`, `${f.MODEL}/${row.id}`)}
              >
                {row.id}
              </Button>
            </TableCell>
            <TableCell>
              {row.name}
            </TableCell>
            <TableCell align="right">
              <DeleteButton element={row} mutate={mutate} store={sourcesStore.strategies} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
  </Table>
  </TableContainer>
  </TableLayout>
  )
}

export default observer(ListStrategies);
