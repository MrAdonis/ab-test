const http = require('node:http');
const { routes } = require('./routes');

const port = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const handler = routes[url.pathname];
  if (!handler) {
    res.writeHead(404, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found' }));
    return;
  }
  handler(req, res);
});

server.listen(port, () => {
  console.log(`relay-api listening on ${port}`);
});
