import polka from 'polka';
import compression from 'compression';
import * as sapper from '@sapper/server';
// import jwt from 'express-jwt';
// import jwksRsa from 'jwks-rsa';
import { SERVER_VARIABLES } from './utils/env-vars';

const { PORT, NODE_ENV } = process.env;
const dev = NODE_ENV === 'development';

const app = polka().use(compression({ threshold: 0 }));

if (dev) {
	app.use(require('sirv')('static', { dev }));
}

console.log(`https://${SERVER_VARIABLES.domain}/.well-known/jwks.json`);
app.use(sapper.middleware())
	// .use(jwt({
	// 	audience: SERVER_VARIABLES.audience,
  	// 	issuer: `https://${SERVER_VARIABLES.domain}/`,
	// 	  algorithms: [ 'RS256' ],
	// 	  secret: jwksRsa.expressJwtSecret({
	// 		cache: true,
	// 		rateLimit: true,
	// 		jwksRequestsPerMinute: 5,
	// 		jwksUri: `https://${SERVER_VARIABLES.domain}/.well-known/jwks.json`
	// 	  })
	// })
	// );

export default app.handler;

if (!process.env.NOW_REGION) {
	app.listen(PORT, err => {
		if (err) console.log('error', err)
	})
}
