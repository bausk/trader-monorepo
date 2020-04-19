import React from 'react';
import { useMemo, useEffect } from 'react';
import App from 'next/app';
import Head from 'next/head';
import merge from 'lodash/merge';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { ThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import auth0 from 'lib/auth0'
import Layout from 'components/layout'
import theme from 'src/theme/index';
import { RootStore, StoreProvider } from 'components/rootStore';
import routes from 'api/frontendRoutes';

export default function MyApp({ Component, pageProps }) {
    const store = useMemo(() => {
        const { initialState } = pageProps;
        if (initialState) {
            return new RootStore(initialState);
        }
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
        window._store = store;
        store.authStore.start();
        return store.authStore.stop;
    }, [])

    useEffect(() => {
        const onLoginChange = (event) => {
            if (event.key === 'login') {
                store.authStore.getUser();
            }
            if (event.key === 'logout') {
                store.authStore.logout('foreignSource');
            }
        }
        window.addEventListener('storage', onLoginChange);
        return () => {
            window.removeEventListener('storage', onLoginChange);
        }
      }, [])

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

MyApp.getInitialProps = async (appContext) => {
    const isServer = (typeof window === 'undefined')
    console.log(`[_app.js] GetInitialProps on ${isServer ? 'server!' : 'browser!'}`);
    if (isServer) {
        const session = await auth0.getSession(appContext.ctx.req);
        appContext.ctx.user = session?.user;
        appContext.ctx.accessToken = session?.accessToken;
    }
    let appProps = {};
    try {
        appProps = await App.getInitialProps(appContext);
    } catch (e) {
        if (isServer) {
            appContext.ctx.res.writeHead(302, {
                Location: routes.HOME,
            })
            return appContext.ctx.res.end();
        }
        window.location.href = routes.HOME;
        return;
    }
    
    let initialState;
    if (isServer) {
        initialState = {
            usersStore: {
                state: "non-fetched",
                users: [],
            },
            sourcesStore: {
                state: "non-fetched",
                sources: ['arrived', 'from', 'SSR'],
            },
            authStore: {
                loading: "fetched",
                user: appContext.ctx.user,
                accessToken: appContext.ctx.accessToken,
            }
        };
    }
    return merge({}, appProps, {pageProps: { initialState }});
};
