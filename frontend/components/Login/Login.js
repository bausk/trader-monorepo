import React from 'react';
import styled from 'styled-components';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Typography from "@material-ui/core/Typography";


class Login extends React.Component {

  state = {
    result: null
  };

  login = (e) => {
    this.props.auth.login();
  }

  logout = (e) => {
    this.props.auth.logout();
  }

  render() {
    const isAuthenticated = this.props.auth && this.props.auth.isAuthenticated;
    return (
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="stretch"
        spacing={16}
      >
        <Grid item>
          <Typography variant="h5" component="h3">Ternovka-2 Landing Page</Typography>
        </Grid>
        <Grid item>
          {isAuthenticated() ?
            <Button variant="contained" color="secondary" onClick={this.logout}>Log Out</Button> :
            <Button variant="contained" color="primary" onClick={this.login}>Log In</Button>
          }
        </Grid>
      </Grid>
    );
  }
}

export default Login;
