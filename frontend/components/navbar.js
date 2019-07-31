import React from 'react';
import Link from 'next/link';
import { connect } from 'react-redux';


class NavBar extends React.Component {
  render() {
    const { user } = this.props;
    const isLoggedIn = !!user.user;
    console.log(user);
    return (
      <header>
        <nav className="navbar" role="navigation" aria-label="main navigation">
          <div className="navbar-brand">
            <a className="navbar-item">
              <img src="/static/logo64.png" />
            </a>
            <a id="burger" onClick={() => (alert('lol not yet'))}
              role="button" className="navbar-burger burger" aria-label="menu" aria-expanded="false" data-target="navbarmenu">
              <span aria-hidden="true"></span>
              <span aria-hidden="true"></span>
              <span aria-hidden="true"></span>
            </a>
          </div>
          <div id="navbarmenu" className="navbar-menu">
            <div className="navbar-start">
              <Link prefetch href="/">
                <a className="navbar-item">Home</a>
              </Link>
              <Link prefetch href="/elsewhere">
                <a className="navbar-item">Elsewhere</a>
              </Link>
            </div>
            <div className="navbar-end">
              <div className="navbar-item">
                <div className="buttons">
                  {isLoggedIn && <Link prefetch href="/logout">
                    <a className="button is-primary">Log Out</a>
                  </Link>}
                  {!isLoggedIn && <Link prefetch href="/login">
                    <a className="button is-primary">Log In</a>
                  </Link>}
                </div>
              </div>
            </div>
          </div>
        </nav>
      </header>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    user: state.user
  }
};

export default connect(mapStateToProps)(NavBar);