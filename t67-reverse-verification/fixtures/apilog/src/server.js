const http = require('http');
const { loadConfig } = require('./config');

const cfg = loadConfig();

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'content-type': 'application/json' });
    return res.end(JSON.stringify({ ok: true }));
  }
  res.writeHead(404);
  res.end();
});

server.listen(cfg.port, () => console.log(`apilog on :${cfg.port}`));
