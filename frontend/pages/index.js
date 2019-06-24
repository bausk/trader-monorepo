import React, { Component } from 'react';
import PropTypes from "prop-types";
import SwipeableViews from "react-swipeable-views";
import styled from 'styled-components';
import Typography from "@material-ui/core/Typography";
import { withStyles } from "@material-ui/core/styles";
import FetchData from '../components/FetchData/FetchDataContainer';
import Header from '../components/Header/Header.js';
import Datasheet from '../components/Datasheet/Datasheet';
import Plot from '../components/Plot/Plot';
import Login from '../components/Login/Login';
import getAuth from '../utils/auth';


const Body = styled(SwipeableViews)`
  padding-top: 20px;
  padding-bottom: 20px;
  text-align: center;
`;

const tabCollection = [
  {
    id: 0,
    title: 'Login',
    component: Login
  },
  {
    id: 1,
    title: 'Data Table',
    component: Datasheet
  },  
  {
    id: 2,
    title: 'Plot 1',
    component: Plot
  }
];

function TabContainer({ children, dir }) {
  return (
    <Typography component="div" dir={dir} style={{ padding: 8 * 3 }}>
      {children}
    </Typography>
  );
}

const styles = theme => ({
  root: {
    backgroundColor: theme.palette.background.paper,
    width: "100%"
  }
});

class App extends Component {
  static propTypes = {
    classes: PropTypes.object.isRequired,
    theme: PropTypes.object.isRequired
  };

  state = {
    ready: false,
    selectedTab: 0
  };

  componentDidMount() {
    this.auth = getAuth();
    this.setState({
      ready: true
    });
  }

  componentDidUpdate() {
    if(!this.auth.isAuthenticated() && !(this.state.selectedTab === 0)) {
      this.setState({selectedTab: 0});
    }
  }

  onSelect = (e, selected) => {
    this.setState({ selectedTab: selected });
  };

  handleChangeIndex = (index) => {
    this.setState({ value: index });
  };

  renderContent = () => {
    const { theme } = this.props;
    return tabCollection.map((tab) => {
      const C = tab.component;
      return <TabContainer
        dir={theme.direction}
        key={tab.id}
      >
        <C auth={this.auth} />
      </TabContainer>;
    });
  };

  render() {
    const { classes, theme } = this.props;

    if (!this.state.ready) {
      return null;
    }
    return (
      <div className={classes.root}>
        <Header
          disabled={!this.auth.isAuthenticated()}
          tabs={tabCollection}
          selected={this.state.selectedTab}
          onSelect={this.onSelect}
        />
        <FetchData isAuthenticated={this.auth.isAuthenticated()} />
        <Body
          axis={theme.direction === "rtl" ? "x-reverse" : "x"}
          index={this.state.selectedTab}
          onChangeIndex={this.handleChangeIndex}
        >
          {this.renderContent()}
        </Body>
      </div>
    );
  }
}

export default withStyles(styles, { withTheme: true })(App);
