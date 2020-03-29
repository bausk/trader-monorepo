import React, { useCallback, useState } from 'react'
import Button from '../components/loadButton';
import auth0 from '../lib/auth0';
import config from '../lib/config';
import { useFetchUser } from '../lib/user';


function Home() {
  const { user, loading } = useFetchUser()
  const [ state, setState ] = useState('None')
  const [ vars, setVars ] = useState('No token obtained so far')
  const callApi = useCallback(
    async () => {
      try {
        let token = '';
        const res = await fetch('/api/gettoken');
        if (res.ok) {
          token = await res.json();
          const response = await fetch("http://localhost:5000/", {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token.accessToken}`
            },
          });
          const payload = await response.json()
          setState(JSON.stringify(payload));
        }
      } catch (e) {
        console.error(e);
      }
    }
    , []);
  return (
    <>
      <h1>Next.js and Auth0 Example</h1>

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
          <Button color="primary">
              Retrieve public data
          </Button>
          <div>{state}</div>
          <div><pre>{vars}</pre></div>
          <p>nickname: {user.nickname}</p>
          <p>name: {user.name}</p>
        </>
      )}
    </>
  )
}

export default Home
