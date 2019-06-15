import polka from 'polka';
import compression from 'compression';
import * as sapper from '@sapper/server';

const { PORT, NODE_ENV } = process.env;
const dev = NODE_ENV === 'development';

const app = polka().use(compression({ threshold: 0 }));

if (dev) {
	app.use(require('sirv')('static', { dev }));
}

app.use(sapper.middleware());

export default app.handler;

if (!process.env.NOW_REGION) {
	app.listen(PORT, err => {
		if (err) console.log('error', err)
	})
}
