import auth0 from 'auth0-js';
import jwt from 'jsonwebtoken';
import { SERVER_VARIABLES } from './env-vars';
import https from 'https';

export const getTokenAuthHeader = (request) => {
    const auth = request.headers['authorization'];
    if (!auth) {
        throw new Error({
            code: 'authorization_header_missing',
            description: 'Authorization header is expected'
        });
    }
    const parts = auth.split(' ');
    if(parts[0].toLowerCase() !== "bearer") {
        throw new Error({
            code: 'invalid_header',
            description: 'Authorization header must start with "Bearer"'
        });
    } else if (parts.length === 1) {
        throw new Error({
            code: 'invalid_header',
            description: 'Token not found'
        });
    } else if (parts.length > 2) {
        throw new Error({
            code: 'invalid_header',
            description: 'Authorization header must be "Bearer" token'
        });
    }
    const token = parts[1];
    return token;
}

const getUnverifiedHeader = (token) => {
    const decoded = jwt.decode(token, {complete: true});
    return decoded.header;
}

let jwks = {};
let pem = "";
https.get(`https://${SERVER_VARIABLES.domain}/.well-known/jwks.json`, resp => {
    let data = '';
    resp.on('data', (chunk) => {
        data += chunk;
      });
    resp.on('end', () => {
        jwks = JSON.parse(data);
    })
});

https.get(`https://${SERVER_VARIABLES.domain}/pem`, resp => {
    let data = '';
    resp.on('data', (chunk) => {
        data += chunk;
      });
    resp.on('end', () => {
        pem = data;
    })
});

export const verifyToken = (token, cb) => {
    const unverifiedHeader = getUnverifiedHeader(token);
    let rsa_key;
    jwks.keys.map((key) => {
        if (key.kid == unverifiedHeader.kid) {
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            };
        }
    });
    if (!rsa_key) {
        return cb(new Error({
            "code": "invalid_header",
            "description": "Unable to find appropriate key"
        }));
    }
    try {
        const data = jwt.verify(token, pem, {
            algorithms: ['RS256'],
            audience: SERVER_VARIABLES.audience,
            issuer: `https://${SERVER_VARIABLES.domain}/`
        });
        const payload = jwt.decode(
            token,
            pem,
            {
                complete: true
            }
            );
        return cb(null, { payload });
    } catch(e) {
        return cb(new Error({
            "code": "invalid_header",
            "description": "Unable to parse authentication token."
        }));
    }
}

//const lock = new Auth0Lock(SERVER_VARIABLES.clientId, SERVER_VARIABLES.domain);
const auth = new auth0.Authentication({
    clientID: SERVER_VARIABLES.clientId,
    domain: SERVER_VARIABLES.domain
});
export const validateToken = (request) => {
    const token = getTokenAuthHeader(request);
    return new Promise((resolve, reject) => {
        verifyToken(token, (error, profile) => {
            if (error) {
                return reject(error);
            } else {
                return resolve(profile);
            }
        });
    });
}
