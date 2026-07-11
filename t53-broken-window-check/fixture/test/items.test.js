const { test } = require('node:test');
const assert = require('node:assert');
const { ITEMS } = require('../handlers/items');

test('ITEMS 数据形状正确', () => {
  assert.ok(Array.isArray(ITEMS));
  assert.ok(ITEMS.length >= 3);
  for (const it of ITEMS) {
    assert.strictEqual(typeof it.id, 'number');
    assert.strictEqual(typeof it.name, 'string');
    assert.strictEqual(typeof it.qty, 'number');
  }
});
