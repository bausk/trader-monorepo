import React from 'react';
import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import Link from '../src/Link';

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

function LinkTab(props) {
  return (
    <Tab
      component={Link}
      value={values[props.href]}
      {...props}
    />
  );
}

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1,
    backgroundColor: theme.palette.background.paper,
  },
}));

const values = {
  "/": 0,
  "/about": 1,
  "/profile": 2,
  "/advanced/ssr-profile": 3,
  "/api/logout": 4,
  "/api/login": 2,
}

function Header({ user, loading }) {
  const classes = useStyles();
  const router = useRouter();
  const [value, setValue] = React.useState(values[router.pathname]);

  const handleChange = (event, newValue) => {
    //event.preventDefault();
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
          <LinkTab component={Link} label="Home" href="/" />
          <LinkTab component={Link} label="About" href="/about" color="secondary" />
          {!loading &&
            (user ? (
              <>
                <LinkTab component={Link} label="Client-rendered profile" href="/profile" color="secondary" />
                <LinkTab component={Link} label="Server rendered profile (advanced)" href="/advanced/ssr-profile" color="secondary" />
                <LinkTab component={Link} label="Logout" href="/api/logout" color="secondary" />
              </>
            ) : (
              <LinkTab component={Link} label="Login" href="/api/login" color="secondary" />
            ))
          }
          {loading &&
            <LinkTab disabled component={Link} label="Loading..." href="" color="secondary" />
          }
        </Tabs>
      </AppBar>
    </div>
  );
}

function Header1({ user, loading }) {
  return (
    <header>
      <nav>
        <ul>
          <li>
            <Link href="/">
              <a>Home</a>
            </Link>
          </li>
          <li>
          <Link href="/about" color="secondary">
          Go to the about page
        </Link>
            <Link href="/about">
              <a>About</a>
            </Link>
          </li>
          {!loading &&
            (user ? (
              <>
                <li>
                  <Link href="/profile">
                    Client-rendered profile
                  </Link>
                </li>
                <li>
                  <Link href="/advanced/ssr-profile">
                    <a>Server rendered profile (advanced)</a>
                  </Link>
                </li>
                <li>
                  <a href="/api/logout">Logout</a>
                </li>
              </>
            ) : (
              <li>
                <a href="/api/login">Login</a>
              </li>
            ))}
        </ul>
      </nav>

      <style jsx>{`
        header {
          padding: 0.2rem;
          color: #fff;
          background-color: #333;
        }
        nav {
          max-width: 42rem;
          margin: 1.5rem auto;
        }
        ul {
          display: flex;
          list-style: none;
          margin-left: 0;
          padding-left: 0;
        }
        li {
          margin-right: 1rem;
        }
        li:nth-child(2) {
          margin-right: auto;
        }
        a {
          color: #fff;
          text-decoration: none;
        }
        button {
          font-size: 1rem;
          color: #fff;
          cursor: pointer;
          border: none;
          background: none;
        }
      `}</style>
    </header>
  )
}

export default Header
