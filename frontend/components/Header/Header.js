import React from 'react';
import PropTypes from "prop-types";
import styled from 'styled-components';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';


class HeaderContainer extends React.Component {
  static propTypes = {
    selected: PropTypes.number,
    onSelect: PropTypes.func,
    disabled: PropTypes.bool
  };

  renderTabs = () => {
    const { tabs } = this.props;
    return tabs.map((tab) => {
      return <Tab label={tab.title} key={tab.id} disabled={this.props.disabled} />
    });
  };

  render() {
    return (
      <AppBar position="static" color="default">
        <Tabs
          value={this.props.selected}
          onChange={this.props.onSelect}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          {this.renderTabs()}
        </Tabs>
      </AppBar>
    );
  }
}

export default HeaderContainer;
