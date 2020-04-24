import React, { useCallback } from 'react';
import useSWR from 'swr';
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import AddIcon from "@material-ui/icons/Add";
import RefreshIcon from "@material-ui/icons/Refresh";
import { observer } from 'mobx-react';
import { useStores } from 'components/rootStore';
import { fetchBackend } from 'api/fetcher';
import r from 'api/backendRoutes';
import Auth from 'api/Auth';

const useStyles = makeStyles({
  table: {
    minWidth: 350
  }
});

function Explore({ sources }) {
  const { sourcesStore, authStore } = useStores();
  const { data, error, mutate } = useSWR(
    () => {
      console.log('[explore] RUN SWR');
      if (typeof window === 'undefined') {
        return;
      }
      if (authStore.accessToken) {
        return '/sources';
      }
      console.log('[explore] RUN SWR FAILED');
      throw new Error();
    },
    async query => await fetchBackend.get(r.SOURCES, authStore.accessToken),
    {
      initialData: sources
    }
  );
  const onAdd = async () => {
    const result = await sourcesStore.addSource();
    mutate(result, false);
  };
  const onRefresh = useCallback(async () => {
    mutate();
  }, []);
  const { user, loading } = authStore;
  const classes = useStyles();
  console.log(data);
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
    <>
      <h1>Sources</h1>
      {loading && <p>Loading login info...</p>}
      <h2>SWR results:</h2>
      <code>{JSON.stringify(data)}</code>
      <code>{JSON.stringify(error)}</code>
      {user && (
        <div className={classes.root}>
          <AppBar position="static">
            <Toolbar>
              <IconButton
                edge="start"
                className={classes.menuButton}
                onClick={onAdd}
                color="inherit"
                aria-label="menu"
              >
                <AddIcon />
              </IconButton>
              <IconButton
                className={classes.menuButton}
                onClick={onRefresh}
                color="inherit"
                aria-label="menu"
              >
                <RefreshIcon />
              </IconButton>
            </Toolbar>
          </AppBar>
          <TableContainer component={Paper}>
            <Table className={classes.table} aria-label="simple table">
              <TableHead>
                <TableRow>
                  <TableCell>Dessert (100g serving)</TableCell>
                  <TableCell align="right">Calories</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map(row => (
                  <TableRow key={row.id}>
                    <TableCell component="th" scope="row">
                      <Button>{row.id}</Button>
                    </TableCell>
                    <TableCell align="right">
                      <Button>{row.type}</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </div>
      )}
    </>
  )
}

Explore.getInitialProps = async ({ req }) => {
    console.log('[explore.js] getting..');
    const token = await Auth.getTokenServerSide(req);
    console.log('[explore.js] token..');
    console.log(token);
    if (token) {
        // should only execute serverside
        const sources = await fetchBackend.get(r.SOURCES, token);
        return {
            fetchedOnServer: true,
            sources: sources,
        }
    }
    return {
        fetchedOnServer: false
    }
};

export default observer(Explore);
