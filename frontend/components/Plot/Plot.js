import React from 'react';
import Grid from '@material-ui/core/Grid';


class PlotContainer extends React.Component {
  render() {
    return (
      <div>
        <Grid
          container
          direction="column"
          justify="center"
          alignItems="stretch"
          spacing={8}
        >
          <div>Dis all so far</div>
        </Grid>
      </div>
    );
  }
}

export default PlotContainer;
