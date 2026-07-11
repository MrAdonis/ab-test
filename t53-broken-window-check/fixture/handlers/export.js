const { ITEMS } = require('./items');

function toCsv(items) {
  const header = 'id,name,qty';
  const rows = items.map((it) => `${it.id},${it.name},${it.qty}`);
  return [header, ...rows].join('\n') + '\n';
}

function exportCsv(req, res) {
  res.writeHead(200, {
    'content-type': 'text/csv',
    'content-disposition': 'attachment; filename="items.csv"',
  });
  res.end(toCsv(ITEMS));
}

module.exports = { toCsv, exportCsv };
