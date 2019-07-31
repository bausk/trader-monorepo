import fetch from 'isomorphic-unfetch';
import { login } from '../../utils/auth';
import { REQUEST_LOGIN, LOGIN_USER, FORGET_USER } from './Login.actions';

const protocol = process.env.NODE_ENV === 'production' ? 'https' : 'http';
const apiAddress = process.env.API_ADDRESS;
const apiUrl = process.browser
    ? `${protocol}://${apiAddress}`
    : `${protocol}://${apiAddress}`;

export default store => next => async (action) => {
    const { type } = action;
    const state = store.getState();
    switch (type) {
        case REQUEST_LOGIN.type: {
            const { token } = action;
            const url = `${apiUrl}/login`;
            try {
              const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token }),
                credentials: 'include'
              });
              if (response.ok) {
                const { token } = await response.json();
                store.dispatch(LOGIN_USER.action(token));
                login({ token });
                return Promise.resolve();
              } else {
                console.log('Login failed.');
                // https://github.com/developit/unfetch#caveats
                let error = new Error(response.statusText);
                error.response = response;
                return Promise.reject(error);
              }
            } catch (error) {
              console.error(
                'You have an error in your code or there are Network issues.',
                error
              );
              return Promise.reject(error);
            }
        }
        default: {
            return next(action);
        }
    }
};
