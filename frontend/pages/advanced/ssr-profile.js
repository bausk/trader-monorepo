import React from 'react'

// This import is only needed when checking authentication status directly from getInitialProps
import { useStores } from '../../components/rootStore';
import { Auth } from '../../components/apiCall';
import { fetchUser } from '../../lib/user';

function Profile() {
    const { authStore } = useStores();
    const { user } = authStore;  
    return (
        <>
        <h1>Profile</h1>

        <div>
            <h3>Profile (server rendered)</h3>
            <img src={user?.picture} alt="user picture" />
            <p>nickname: {user?.nickname}</p>
            <p>name: {user?.name}</p>
        </div>
        </>
    )
}

// Profile.getInitialProps = async ({ req, res }) => {
//   // On the server-side you can check authentication status directly
//   // However in general you might want to call API Routes to fetch data
//   // An example of directly checking authentication:
//   if (typeof window === 'undefined') {
//         const session = await auth0.getSession(req)
//         if (!session?.user) {
//             res.writeHead(302, {
//                 Location: '/api/login',
//             })
//             res.end()
//             return
//         }
//         return { user: session?.user }
//     }


//     // To do fetches to API routes you can pass the cookie coming from the incoming request on to the fetch
//     // so that a request to the API is done on behalf of the user
//     // keep in mind that server-side fetches need a full URL, meaning that the full url has to be provided to the application
//     const cookie = req && req.headers.cookie


//     const user = await fetchUser(cookie)

//     // A redirect is needed to authenticate to Auth0
//     if (!user) {
//         if (typeof window == 'undefined') {
//         res.writeHead(200, {
//             //Location: '/api/login',
//         })
//         return res.end()
//         }

//         window.location.href = '/api/login'
//     }

//     return { user }
//     }



Profile.getInitialProps = async ({ req, res, user }) => {
    // On the server-side you can check authentication status directly
    // However in general you might want to call API Routes to fetch data
    // An example of directly checking authentication:
  
    //vs
    const isServer = typeof window === 'undefined';
    // To do fetches to API routes you can pass the cookie coming from the incoming request on to the fetch
    // so that a request to the API is done on behalf of the user
    // keep in mind that server-side fetches need a full URL, meaning that the full url has to be provided to the application

    if (isServer) {
        // if (!user) {
        //     debugger;
        //     res.writeHead(302, {
        //         Location: '/api/login',
        //     })
        //     return res.end();
        // }
        const cookie = req && req.headers.cookie
        // try {
            const newUser = await Auth.getprofile(cookie);
            return {
                pageProps: {
                    initialState: {
                        authStore: {
                            user: newUser
                        }
                    }
                }
            }
        // }
        // catch (e) {
        //     res.writeHead(302, {
        //         Location: '/api/login',
        //     })
        //     return res.end();
        // }
    }

    
    

    // A redirect is needed to authenticate to Auth0
    if (!newUser) {
        if (isServer) {
        res.writeHead(302, {
            Location: '/api/login',
        })
        return res.end()
        }
        window.location.href = '/api/login'
    }
}

export default Profile