import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';


const useStyles = makeStyles({
  depositContext: {
    flex: 1,
  },
});

export default function ActiveSessionProperties({session}) {
  const classes = useStyles();
  return (
    <React.Fragment>
      <Typography component="h2" variant="h6" color="primary" gutterBottom>Session is {session ? 'active' : 'inactive'}</Typography>
      {session &&
        (<><Typography component="p" variant="h4">
            ${session?.amount}
        </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        started on {session?.start_datetime}
      </Typography>
      <div>
        <Typography color="primary">
          View balance
        </Typography>
      </div></>)
      }
    </React.Fragment>
  );
}
