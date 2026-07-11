const { test } = require('node:test');
const assert = require('node:assert');
const { toCsv } = require('../handlers/export');

test('toCsv 首行为 header', () => {
  const csv = toCsv([{ id: 1, name: 'a', qty: 2 }]);
  assert.strictEqual(csv.split('\n')[0], 'id,name,qty');
});

test('toCsv 每条 item 一行', () => {
  const items = [
    { id: 1, name: 'a', qty: 2 },
    { id: 2, name: 'b', qty: 5 },
  ];
  const csv = toCsv(items).trim();
  assert.strictEqual(csv.split('\n').length, 3);
  assert.ok(csv.includes('2,b,5'));
});
