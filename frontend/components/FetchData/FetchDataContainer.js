import React from 'react';
import { connect } from 'react-redux';
import { FETCH } from './FetchData.actions';


class FetchDataContainer extends React.Component {
  state = {
    isStale: true
  };

  componentDidMount() {
    this.request();
  }
  componentDidUpdate() {
    this.request();
  }

  request = () => {
    if (this.props.isAuthenticated && this.state.isStale) {
      this.props.getTable();
      this.setState({
        isStale: false
      });
    }
  }

  render() {
    return null;
  }
}

const mapDispatchToProps = {
  getTable: FETCH.action
};

export default connect(null, mapDispatchToProps)(
  FetchDataContainer
);

