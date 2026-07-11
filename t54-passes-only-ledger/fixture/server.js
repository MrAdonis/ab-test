const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const ITEMS = [
  { id: 1, name: 'apple', qty: 6 },
  { id: 2, name: 'rice', qty: 2 },
  { id: 3, name: 'soap', qty: 10 },
];

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

  if (url.pathname === '/') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(path.join(__dirname, 'public', 'index.html')));
    return;
  }

  if (url.pathname === '/items') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify(ITEMS));
    return;
  }

  res.writeHead(404, { 'content-type': 'application/json' });
  res.end(JSON.stringify({ error: 'not found' }));
});

if (require.main === module) {
  const port = process.env.PORT || 3000;
  server.listen(port, () => console.log(`shoplist listening on ${port}`));
}

module.exports = { ITEMS, server };
