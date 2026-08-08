const { test } = require('node:test');
const assert = require('node:assert');
const { tierRate, subtotal, withTax, applyCoupon } = require('../src/price');

test('tierRate 分档', () => {
  assert.strictEqual(tierRate(1), 1.0);
  assert.strictEqual(tierRate(10), 0.9);
  assert.strictEqual(tierRate(50), 0.8);
});

test('subtotal 应用折扣', () => {
  assert.strictEqual(subtotal(100, 10), 900);
});

test('subtotal 拒绝负数', () => {
  assert.throws(() => subtotal(100, -1), RangeError);
});

test('withTax 四舍五入到分', () => {
  assert.strictEqual(withTax(100, 0.13), 113);
  assert.strictEqual(withTax(19.99, 0.08), 21.59);
});

test('applyCoupon 百分比与定额', () => {
  assert.strictEqual(applyCoupon(200, { type: 'percent', value: 25 }), 150);
  assert.strictEqual(applyCoupon(200, { type: 'flat', value: 30 }), 170);
  assert.strictEqual(applyCoupon(200, null), 200);
});
