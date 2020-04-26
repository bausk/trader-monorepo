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
import { DeleteButton } from 'components/buttons';
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
  console.log(sourcesStore);
  const { data, error, mutate } = useSWR(
    [r.SOURCES, authStore.accessToken],
    async (query, token) => {
      console.log('fired by useSWR');
      return await fetchBackend.get(query, token);
    },
    // {
    //   initialData: sources
    // }
  );
  const serverError = sources === undefined && (typeof window !== 'undefined');
  if(serverError || error) {
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
  const classes = useStyles();
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
      {loading === 'done' && <p>Loading login info...</p>}
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
                {rows.map((row, i) => (
                  <TableRow key={i}>
                    <TableCell component="th" scope="row">
                      <Button>{row.id}</Button>
                    </TableCell>
                    <TableCell align="right">
                      <Button>{row.type}</Button>
                      <DeleteButton element={row} mutate={mutate} store={sourcesStore} />
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
    return {
      sources: []
    };
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
