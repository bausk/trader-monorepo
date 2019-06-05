import sirv from 'sirv';
import polka from 'polka';
import compression from 'compression';
import * as sapper from '@sapper/server';

const { PORT, NODE_ENV } = process.env;
const dev = NODE_ENV === 'development';

const app = polka() // You can also use Express
	.use(compression({ threshold: 0 }));

if (dev) {
	app.use(sirv('static', { dev }));
}

app.use(sapper.middleware())
	.listen(PORT, err => {
		if (err) console.log('error', err);
	});

module.exports = app.handler;
