import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';


const useStyles = makeStyles({
  depositContext: {
    flex: 1,
  },
});

export default function ModelProperties({model}) {
  const classes = useStyles();
  const config = JSON.parse(model?.config_json || '{}');
  return (
    <React.Fragment>
      <Typography component="h2" variant="h6" color="primary" gutterBottom>Model Properties:</Typography>
      <Typography component="p" variant="h6">
          Name: {model?.name} ({model?.id})
      </Typography>
      <Typography component="p" variant="h6">
          Type: {model?.typename}
      </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        Strategy name: {config.strategy_name || "N/A"}
      </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        Executor: {config.order_executor || "N/A"}
      </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        Primary Source: {config.source_primary || "N/A"}
      </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        Secondary Source: {config.source_secondary || "N/A"}
      </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        Tick Resolution: {config.tick_frequency || "N/A"} seconds
      </Typography>
    </React.Fragment>
  );
}
