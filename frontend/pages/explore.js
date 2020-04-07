import React, { useCallback, useState, useContext } from 'react'
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
import Typography from "@material-ui/core/Typography";
import Link from "next/link";
import { observer } from 'mobx-react';
import { useFetchUser } from '../lib/user';
import { useStores } from '../components/rootStore';

const useStyles = makeStyles({
  table: {
    minWidth: 350
  }
});

function Explore() {
  const { user, loading } = useFetchUser();
  const { sourcesStore } = useStores();
  const classes = useStyles();
  const rows = sourcesStore.sources;
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
      {user && (
        <div className={classes.root}>
          <AppBar position="static">
            <Toolbar>
              <IconButton
                edge="start"
                className={classes.menuButton}
                color="inherit"
                aria-label="menu"
              >
                <AddIcon />
              </IconButton>
              <IconButton
                className={classes.menuButton}
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
                  <TableRow key={row}>
                    <TableCell component="th" scope="row">
                      <Button>{row}</Button>
                    </TableCell>
                    <TableCell align="right">
                      <Button>{row}</Button>
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

export default observer(Explore);
