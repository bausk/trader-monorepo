import React from 'react';
import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';

import r from 'api/frontendRoutes';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <Typography
      component="div"
      role="tabpanel"
      hidden={value !== index}
      id={`nav-tabpanel-${index}`}
      aria-labelledby={`nav-tab-${index}`}
      {...other}
    >
      {value === index && <Box p={3}>{children}</Box>}
    </Typography>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.any.isRequired,
  value: PropTypes.any.isRequired,
};

function a11yProps(index) {
  return {
    id: `nav-tab-${index}`,
    'aria-controls': `nav-tabpanel-${index}`,
  };
}

const useStyles = makeStyles(theme => ({
  // root: {
  //   flexGrow: 1,
  //   backgroundColor: theme.palette.background.paper,
  // },
}));


function Header() {
  const classes = useStyles();
  const router = useRouter();
  const [value, setValue] = React.useState(router.pathname);
  const activeTabValue = '/' + value.split('/')[1];
  const handleChange = (event, newValue) => {
    event.preventDefault();
    router.push(newValue);
    setValue(newValue);
  };
  return (
    <div className={classes.root}>
      <AppBar position="static">
        <Tabs
          variant="fullWidth"
          value={activeTabValue}
          onChange={handleChange}
          aria-label="nav tabs example"
        >
          <Tab value={r.HOME} label="Dashboard" href={r.HOME} {...a11yProps(0)} />
          <Tab value={r.EXPLORE} label="Explore" href={r.EXPLORE} {...a11yProps(1)} />
          <Tab disabled value={r.MODEL} label="Model" href={r.MODEL} {...a11yProps(2)} />
          <Tab disabled value={r.OPTIMIZE} label="Optimize" href={r.OPTIMIZE} {...a11yProps(3)} />
          <Tab disabled value={r.TRADE} label="Trade" href={r.TRADE} {...a11yProps(4)} />
          <Tab value={r.PROFILE} label="Profile" href={r.PROFILE} {...a11yProps(5)} />
          <Tab value={r.SERVERPROFILE} label="SSR-Profile" href={r.SERVERPROFILE} {...a11yProps(6)} />
        </Tabs>
      </AppBar>
    </div>
  );
}

export default Header
