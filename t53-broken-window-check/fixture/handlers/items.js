const ITEMS = [
  { id: 1, name: 'relay-board', qty: 12 },
  { id: 2, name: 'power-module', qty: 3 },
  { id: 3, name: 'sensor-kit', qty: 27 },
];

function listItems(req, res) {
  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify(ITEMS));
}

module.exports = { ITEMS, listItems };
