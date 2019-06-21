// import { createBrowserHistory } from 'history';
import { CLIENT_VARIABLES } from './env-vars';

export default async () => {
  const { createBrowserHistory } = await import('history');
  // const { Auth0Lock } = await import('auth0-lock');

  class Auth {
    constructor() {
      this.lock = new Auth0Lock(CLIENT_VARIABLES.clientId, CLIENT_VARIABLES.domain, {
        autoclose: true,
        allowSignUp: false,
        auth: {
          redirectUrl: CLIENT_VARIABLES.callbackUrl,
          responseType: 'token id_token',
          audience: CLIENT_VARIABLES.audience,
          params: {
            scope: 'openid profile email'
          }
        }
      });
      this.handleAuthentication();
      // binds functions to keep this context
      this.login = this.login.bind(this);
      this.logout = this.logout.bind(this);
      this.isAuthenticated = this.isAuthenticated.bind(this);
      this.history = createBrowserHistory({
        forceRefresh: true
      });
    }

    login() {
      // Call the show method to display the widget.
      this.lock.show({language: 'ru'});
    }

    getAccessToken() {
      return localStorage.getItem('access_token');
    }

    handleAuthentication() {
      // Add a callback for Lock's `authenticated` event
      this.lock.on('authenticated', this.setSession.bind(this));
      // Add a callback for Lock's `authorization_error` event
      this.lock.on('authorization_error', (err) => {
        console.log(err);
        alert(`Error: ${err.error}. Check the console for further details.`);
        this.history.replace('/');
      });
    }

    setSession(authResult) {
      if (authResult && authResult.accessToken && authResult.idToken) {
        // Set the time that the access token will expire at
        let expiresAt = JSON.stringify((authResult.expiresIn * 1000) + new Date().getTime());
        localStorage.setItem('access_token', authResult.accessToken);
        localStorage.setItem('id_token', authResult.idToken);
        localStorage.setItem('expires_at', expiresAt);
        // navigate to the home route
        this.history.replace('/');
      }
    }

    logout() {
      // Clear access token and ID token from local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('id_token');
      localStorage.removeItem('expires_at');
      // navigate to the home route
      this.history.replace('/');
    }

    isAuthenticated() {
      // Check whether the current time is past the 
      // access token's expiry time
      let expiresAt = JSON.parse(localStorage.getItem('expires_at'));
      return new Date().getTime() < expiresAt;
    }
  }

  let auth;


  if (!auth && !!window) {
    auth = new Auth();
  }
  return auth;
};