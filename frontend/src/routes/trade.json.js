const contents = JSON.stringify({
	message: 'this is a secret!'
});

export function get(req, res) {
	res.writeHead(200, {
		'Content-Type': 'application/json'
	});

	res.end(contents);
}