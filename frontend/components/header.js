import React from 'react';
import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import path from '../src/content/routes';

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


function Header({ user, loading }) {
  const classes = useStyles();
  const router = useRouter();
  const [value, setValue] = React.useState(router.pathname);

  const handleChange = (event, newValue) => {
    event.preventDefault();
    console.log(newValue);
    router.push(newValue);
    setValue(newValue);
  };
  const label = user ? 'Logout' : 'Login';
  const link = user ? path.LOGOUT : path.LOGIN;
  return (
    <div className={classes.root}>
      <AppBar position="static">
        <Tabs
          variant="fullWidth"
          value={value}
          onChange={handleChange}
          aria-label="nav tabs example"
        >
          <Tab value={path.HOME} label="Dashboard" href={path.HOME} {...a11yProps(0)} />
          <Tab value={path.ABOUT} label="About" href={path.ABOUT} textColor="secondary" {...a11yProps(1)} />
          <Tab value={path.PROFILE} label="Client-rendered profile" href={path.PROFILE} {...a11yProps(2)} />
          <Tab value={path.SERVERPROFILE} label="Server-rendered profile" href={path.SERVERPROFILE} {...a11yProps(3)} />
          <Tab value={link} label={label} href={link} {...a11yProps(4)} />
        </Tabs>
      </AppBar>
    </div>
  );
}

export default Header
