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
import { useStores } from 'components/rootStore';
import { DeleteButton } from 'components/buttons';
import { fetchBackend } from 'api/fetcher';
import r from 'api/backendRoutes';
import f from 'api/frontendRoutes';
import Auth from 'api/Auth';

function Explore() {
  const { sourcesStore, authStore } = useStores();
  const router = useRouter();
  const { data, error, mutate } = useSWR(
    [r.SOURCES],
    async () => {
      console.log('fired by useSWR');
      return await sourcesStore.list();
    }
  );
  if(error) {
    authStore.login();
  }
  const onAdd = useCallback(async () => {
    const newSource = {
      id: undefined,
      type: 'тож хз',
    }
    mutate(async (prev) => [...prev, newSource], false);
    mutate(sourcesStore.add());
  }, [data, mutate, sourcesStore.add]);
  const onRefresh = useCallback(async () => {
    mutate();
  }, [mutate]);
  const { user, loading } = authStore;
  const rows = data || [];
  if (!loading && !user) {
    return (
      <>
        <p>
          To test the login click in <i>Login</i>
        </p>
        <p>
          Once you have logged in you should be able to click in{' '}
          <i>Profile</i> and <i>Logout</i>
        </p>
      </>
    );
  }
  
  return (
    <TableLayout
      title="Sources"
      toolbar={() => (
        <>
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
          <TableCell>Type</TableCell>
          <TableCell align="right">Operations</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((row, i) => (
          <TableRow key={i}>
            <TableCell component="th" scope="row">
              <Button
                onClick={() => router.push(`${f.EXPLORE}/${row.id}`)}
              >
                {row.id}
              </Button>
            </TableCell>
            <TableCell>
              {row.type}
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

Explore.getInitialProps = async ({ req }) => {
    return {
      sources: []
    };
    // Example SSR implementation
    const token = await Auth.getTokenServerSide(req);
    if (token) {
        // should only execute serverside
        const sources = await fetchBackend.get(r.SOURCES, token);
        return {
            sources
        }
    }
    if (typeof window !== 'undefined') {
      return {
          sources: []
      }
    }
};

export default observer(Explore);
