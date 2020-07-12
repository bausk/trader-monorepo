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
import NewEntityModal from 'components/Modals/NewEntityModal';
import { useStores } from 'components/rootStore';
import { DeleteButton } from 'components/buttons';
import b from 'api/backendRoutes';
import f from 'api/frontendRoutes';


function SourcesList() {
  const { sourcesStore, authStore } = useStores();
  const router = useRouter();
  const { data, error, mutate } = useSWR(
    b.SOURCES,
    sourcesStore.list
  );
  if(error) {
    authStore.login();
  }
  const newModal = router.asPath === f.EXPLORE_NEW;
  const onAdd = useCallback(async () => {
    return router.push(f.EXPLORE, f.EXPLORE_NEW);
  }, [router]);
  const onSubmit = useCallback(async (result) => {
    const newSource = {
      id: undefined,
      name: result.name,
      typename: result.sourceType,
      config_json: JSON.stringify({
        table_name: result.tableName
      }),
    }
    mutate(async (prev) => [...prev, newSource], false);
    mutate(sourcesStore.add(newSource));
  }, [mutate, sourcesStore.add]);
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
      title="Sources"
      toolbar={() => (
        <>
          <NewEntityModal
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
          <TableCell>Source ID</TableCell>
          <TableCell>Name</TableCell>
          <TableCell>Type</TableCell>
          <TableCell align="right">Operations</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((row, i) => (
          <TableRow key={i}>
            <TableCell component="th" scope="row">
              <Button
                onClick={() => router.push(`${f.EXPLORE}/[id]`, `${f.EXPLORE}/${row.id}`)}
              >
                {row.id}
              </Button>
            </TableCell>
            <TableCell>
              {row.name}
            </TableCell>
            <TableCell>
              {row.typename}
            </TableCell>
            <TableCell align="right">
              <DeleteButton element={row} mutate={mutate} store={sourcesStore} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
  </Table>
  </TableContainer>
  </TableLayout>
  )
}

export default observer(SourcesList);
