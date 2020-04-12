import React from 'react'
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react'
import ApiButton from '../components/loadButton';
import { useStores } from '../components/rootStore';


function Home() {
  const { sourcesStore, authStore } = useStores();
  const { loading, user } = authStore;
  const isLoading = loading === 'fetching';
  const label = isLoading ? 'Pending...' : (user  ? 'Logout' : 'Login');
  const onLoginStateChange = React.useCallback(() => {
    if (user) {
      authStore.logout();
    } else {
      authStore.login();
    }
  }, [authStore, user]);
  return (
    <>
      <h1>Next.js and Auth0 Example</h1>

        <Button
          component="a"
          onClick={onLoginStateChange}
          disabled={isLoading}
          color="primary"
          variant="contained"
        >
          {label}
        </Button>

      {isLoading && <p>Loading login info...</p>}

      {!isLoading && !user && (
        <>
          <p>
            To test the login click in <i>Login</i>
          </p>
          <p>
            Once you have logged in you should be able to click in{' '}
            <i>Profile</i> and <i>Logout</i>
          </p>
        </>
      )}

      {user && (
        <>
          <h4>Rendered user info on the client</h4>
          <img src={user.picture} alt="user picture" />
          <br />
          <ApiButton color="primary" variant="outlined">
              Retrieve public data
          </ApiButton>
          <div>{JSON.stringify(sourcesStore.sources)}</div>
          <p>nickname: {user.nickname}</p>
          <p>name: {user.name}</p>
        </>
      )}
    </>
  )
}

export default observer(Home);
