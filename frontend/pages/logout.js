import React from 'react';
import { destroyCookie } from 'nookies';
import Router from 'next/router';
import { FORGET_USER } from '../components/Login/Login.actions';

class Logout extends React.Component {
  static async getInitialProps(ctx) {
    destroyCookie(ctx, 'token');
    destroyCookie(ctx, 'AIOHTTP_SESSION');
    const store = ctx.reduxStore;
    store.dispatch(FORGET_USER.action());
    if (ctx.req) {
      ctx.res.writeHead(302, { Location: '/login' });
      ctx.res.end();
    }
    Router.push('/login');
    return {};
  }
  render() {
    return null;
  }
}

export default Logout;
