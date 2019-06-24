import App, { Container } from 'next/app'
import React from 'react'
import Head from "next/head";
import { Provider } from 'react-redux'
import MomentUtils from '@date-io/moment';
import { MuiPickersUtilsProvider } from 'material-ui-pickers';
import withReduxStore from '../lib/with-redux-store'


class MyApp extends App {
  renderHead() {
    return (
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css?family=Roboto:300,400,500"
        />
      </Head>
    );
  }

  render () {
    const { Component, pageProps, reduxStore } = this.props
    return (
      <MuiPickersUtilsProvider utils={MomentUtils}>
        <Container>
          {this.renderHead()}
          <Provider store={reduxStore}>
            <Component {...pageProps} />
          </Provider>
        </Container>
      </MuiPickersUtilsProvider>
    )
  }
}

export default withReduxStore(MyApp)