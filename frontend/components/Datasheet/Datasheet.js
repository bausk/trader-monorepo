import React from 'react';
import { connect } from 'react-redux';
import Grid from '@material-ui/core/Grid';
import Typography from "@material-ui/core/Typography";
import Table from '../Table/Table';


class Datasheet extends React.Component {
  render() {
    return (
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="stretch"
        spacing={16}
      >
        <Grid item>
          <Typography variant="h5" component="h3">Ternovka -- Data Chart</Typography>
        </Grid>
        <Grid item>
          <Table data={this.props.data} header={this.props.header} />
        </Grid>
      </Grid>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    data: state.table.normalizedData,
    header: state.table.header
  };
};

export default connect(mapStateToProps)(Datasheet);
