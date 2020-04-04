import React from 'react'
import Link from "next/link";
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react'
import ApiButton from '../components/loadButton';
import { useFetchUser } from '../lib/user';
import path from '../src/content/routes';
import { useStores } from '../components/rootStore';


function Home() {
  const { user, loading } = useFetchUser();
  const { usersStore } = useStores();
  const label = user ? 'Logout' : (loading ? 'Pending...' : 'Login');
  const link = user ? path.LOGOUT : path.LOGIN;
  return (
    <>
      <h1>Next.js and Auth0 Example</h1>

      <Link href={link} passHref>
        <Button
          component="a"
          disabled={loading}
          color="primary"
          variant="contained"
        >
          {label}
        </Button>
      </Link>

      {loading && <p>Loading login info...</p>}

      {!loading && !user && (
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
          <ApiButton color="primary" variant="outlined">
              Retrieve public data
          </ApiButton>
          <div>{usersStore.getSources()}</div>
          <p>nickname: {user.nickname}</p>
          <p>name: {user.name}</p>
        </>
      )}
    </>
  )
}

export default observer(Home);
