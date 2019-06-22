// import { validateToken } from '../utils/authValidate';

export function get(req, res) {
	res.writeHead(200, {
		'Content-Type': 'application/json'
	});
	console.log(req.user);
	debugger;
	const contents = JSON.stringify({
		message: JSON.stringify(req.user)
	});
	return res.end(contents);
}