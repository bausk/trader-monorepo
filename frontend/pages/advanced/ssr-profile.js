import React, { useEffect } from 'react';
import { observer } from 'mobx-react';
// This import is only needed when checking authentication status directly from getInitialProps
import { useStores } from 'components/rootStore';
import Auth from 'api/Auth';

function Profile({ fetchedOnServer, user }) {
    const { authStore } = useStores();
    useEffect(() => {
        if (!fetchedOnServer) {
            // TODO: handle exception?
            authStore.getUser();
        }
    }, [])
    const userToShow = user || authStore.user;
    return (
        <>
            <h1>Profile</h1>

            <div>
                <h3>Profile (server rendered)</h3>
                <img src={userToShow?.picture} alt="user picture" />
                <p>nickname: {userToShow?.nickname}</p>
                <p>name: {userToShow?.name}</p>
            </div>
        </>
    )
}

Profile.getInitialProps = async ({ req }) => {
    const user = await Auth.checkLogin(req);
    if (user) {
        return {
            fetchedOnServer: true,
            user: newUser,
        }
    }
    return {
        fetchedOnServer: false
    }
}

export default observer(Profile);
