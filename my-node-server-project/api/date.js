const http = require('http');
const moment = require('moment');

const server = http.createServer((req, res) => {
  res.writeHeader(200, { 'Content-Type': 'text/html' });
  const currentTime = moment().format('MMMM Do YYYY, h:mm:ss a');
  res.end(currentTime);
});

server.listen();
