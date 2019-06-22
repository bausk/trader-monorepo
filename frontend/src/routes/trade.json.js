import { validateToken } from '../utils/authValidate';

export function get(req, res) {
	res.writeHead(200, {
		'Content-Type': 'application/json'
	});
	
	validateToken(req).then((profile) => {
		const contents = JSON.stringify({
			message: JSON.stringify(profile)
		});
		return res.end(contents);
	}).catch((err) => {
		return res.end(JSON.stringify({
			message: 'psa poperdolilo'
		}));
	});

}