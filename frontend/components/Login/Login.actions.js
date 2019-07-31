
export const REQUEST_LOGIN = {
    type: 'REQUEST_LOGIN',
    action: (token) => ({
        type: 'REQUEST_LOGIN',
        token
    })
};

export const LOGIN_USER = {
    type: 'LOGIN_USER',
    action: (user) => ({
        type: 'LOGIN_USER',
        user
    })
};

export const FORGET_USER = {
    type: 'FORGET_USER',
    action: () => ({
        type: 'FORGET_USER'
    })
};