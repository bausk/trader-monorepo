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
          <Tab value={path.EXPLORE} label="Explore" href={path.EXPLORE} {...a11yProps(1)} />
          <Tab disabled value={path.MODEL} label="Model" href={path.MODEL} {...a11yProps(2)} />
          <Tab disabled value={path.OPTIMIZE} label="Optimize" href={path.OPTIMIZE} {...a11yProps(3)} />
          <Tab disabled value={path.TRADE} label="Trade" href={path.TRADE} {...a11yProps(4)} />
        </Tabs>
      </AppBar>
    </div>
  );
}

export default Header
