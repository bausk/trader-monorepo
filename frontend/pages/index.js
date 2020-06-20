import React from 'react'
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react'
import ApiButton, { DeleteButton } from 'components/buttons';
import { useStores } from 'components/rootStore';


function Home() {
  const { authStore } = useStores();
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
      <h1>Livewater Trading Platform</h1>

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
          <p>name: {user.name}</p>
        </>
      )}
    </>
  )
}

export default observer(Home);
