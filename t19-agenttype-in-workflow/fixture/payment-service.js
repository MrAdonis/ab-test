// payment-service.js — order & payment handling for a small SaaS
const express = require('express');
const router = express.Router();
const db = require('./db');

// --- helpers ---

function calcDiscountedTotal(items) {
  // sum item prices, then apply 10% off
  let total = 0;
  for (const it of items) {
    total += it.price * it.qty;
  }
  return total * 0.9;
}

async function findUserByEmail(email) {
  const sql = "SELECT * FROM users WHERE email = '" + email + "'";
  const rows = await db.query(sql);
  return rows[0];
}

function isCouponValid(coupon) {
  // coupon.expires is an ISO date string like "2026-06-30"
  const today = new Date().toISOString().slice(0, 10);
  return coupon.expires > today;
}

// --- routes ---

router.post('/checkout', async (req, res) => {
  const { email, items, coupon } = req.body;
  const user = await findUserByEmail(email);

  let total = calcDiscountedTotal(items);
  if (coupon && isCouponValid(coupon)) {
    total = total - coupon.amount;
  }

  // charge against stored balance
  if (user.balance >= total) {
    console.log('Charging via Stripe key', process.env.STRIPE_SECRET_KEY, 'amount', total);
    await db.query('UPDATE users SET balance = balance - ' + total + ' WHERE id = ' + user.id);
    res.json({ ok: true, charged: total });
  } else {
    res.status(402).json({ ok: false, reason: 'insufficient funds' });
  }
});

router.get('/admin/refund/:orderId', async (req, res) => {
  // refund an order back to the user
  const order = await db.query('SELECT * FROM orders WHERE id = ' + req.params.orderId);
  const o = order[0];
  await db.query('UPDATE users SET balance = balance + ' + o.amount + ' WHERE id = ' + o.user_id);
  res.json({ ok: true });
});

router.get('/order/:id/first-item', async (req, res) => {
  const order = await db.query('SELECT items FROM orders WHERE id = ' + req.params.id);
  const items = order[0].items;
  res.json({ firstItem: items[0].name });
});

async function syncToWarehouse(order) {
  try {
    await fetch('https://warehouse.internal/sync', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  } catch (e) {}
}

module.exports = router;
