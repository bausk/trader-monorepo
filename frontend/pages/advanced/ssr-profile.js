import React, { useEffect } from 'react';
import { observer } from 'mobx-react';
// This import is only needed when checking authentication status directly from getInitialProps
import { useStores } from 'components/rootStore';
import Auth from 'api/Auth';

function Profile({ fetchedOnServer, user }) {
    const { authStore } = useStores();
    useEffect(() => {
        if (!fetchedOnServer) {
            console.log('fetching on client!');
            // Todo: handle exception?
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

// export async function getServerSideProps(context) {
//     console.log(`ururu will fetch on server ${typeof window}`);
//     return {
//         props: {
//             fetchedOnServer: true,
//             user: {
//                 nickname: "kekmaster",
//                 name: "blohart"
//             }
//         }, // will be passed to the page component as props
//     }
// }

Profile.getInitialProps = async ({ req, res, user }) => {

    const isServer = typeof window === 'undefined';

    if (isServer) {
        const cookie = req && req.headers.cookie
        const newUser = await Auth.getprofile(cookie);
        if (!newUser) {
            throw new Error('user not available');
        }
        return {
            fetchedOnServer: true,
            user: newUser,
        }
    }
    return {
        fetchedOnServer: false
    }

    
    

    // A redirect is needed to authenticate to Auth0
    // if (!newUser) {
    //     if (isServer) {
    //     res.writeHead(302, {
    //         Location: '/api/login',
    //     })
    //     return res.end()
    //     }
    //     window.location.href = '/api/login'
    // }
}

export default observer(Profile);