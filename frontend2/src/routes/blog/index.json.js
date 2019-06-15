import posts from './_posts.js';

const contents = JSON.stringify(posts.map(post => {
	return {
		title: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15),
		slug: post.slug
	};
}));

export function get(req, res) {
	res.writeHead(200, {
		'Content-Type': 'application/json'
	});

	res.end(contents);
}