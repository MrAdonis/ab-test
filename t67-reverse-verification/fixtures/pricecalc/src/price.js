const TIERS = [
  { min: 0, rate: 1.0 },
  { min: 10, rate: 0.9 },
  { min: 50, rate: 0.8 },
];

function tierRate(qty) {
  let rate = 1.0;
  for (const t of TIERS) if (qty >= t.min) rate = t.rate;
  return rate;
}

function subtotal(unitPrice, qty) {
  if (qty < 0) throw new RangeError('qty must be >= 0');
  return unitPrice * qty * tierRate(qty);
}

function withTax(amount, taxRate) {
  return Math.round(amount * (1 + taxRate) * 100) / 100;
}

function applyCoupon(amount, coupon) {
  if (!coupon) return amount;
  if (coupon.type === 'percent') return amount * (1 - coupon.value / 100);
  if (coupon.type === 'flat') return Math.max(0, amount - coupon.value);
  throw new Error('unknown coupon type: ' + coupon.type);
}

module.exports = { tierRate, subtotal, withTax, applyCoupon };
