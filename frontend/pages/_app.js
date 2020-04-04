import React from 'react';
import App from 'next/app';
import Head from 'next/head';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { ThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Layout from '../components/layout'
import theme from '../src/theme';

import { useMemo, useEffect } from 'react';
import { RootStore, StoreProvider } from '../components/rootStore';


export default function MyApp({ Component, pageProps }) {
    const store = useMemo(() => {
        return new RootStore();
    }, []);

    useEffect(() => {
        // Remove the server-side injected CSS.
        const jssStyles = document.querySelector('#jss-server-side');
        if (jssStyles) {
          jssStyles.parentElement.removeChild(jssStyles);
        }
    }, []);

    useEffect(() => {
        // If your page has Next.js data fetching methods returning a state for the Mobx store,
        // then you can hydrate it here.
        const { initialState } = pageProps;
        if (initialState) {
            store.hydrate(initialState);
        }
    }, [store, pageProps]);

    return (
        <>
            <Head>
                <title>My page</title>
                <meta name="viewport" content="minimum-scale=1, initial-scale=1, width=device-width" />
            </Head>
            <ThemeProvider theme={theme}>
            <StyledThemeProvider theme={theme}>
                {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
                <CssBaseline />
                <Layout>
                <StoreProvider store={store}>
                    <Component {...pageProps} />
                </StoreProvider>
                </Layout>
            </StyledThemeProvider>
            </ThemeProvider>
        </>
    );
};


MyApp.getInitialProps = async (ctx) => {
    console.log(`GetInitialProps on ${(typeof window === 'undefined') ? 'server!' : 'browser!'}`);
    const appProps = await App.getInitialProps(ctx);
    const initialState = {
        user: null,
        todos: [
            'one',
            'two'
        ]
    };
    return {
        ...appProps,
        pageProps: {
            initialState
        }
    };
};
