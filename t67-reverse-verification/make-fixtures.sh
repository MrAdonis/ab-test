#!/bin/bash
# 生成 t67 两个任务的 fixture 母本（每个 run 从母本 cp -r 到独立 mktemp 沙箱）
set -eu
BASE="$(cd "$(dirname "$0")" && pwd)/fixtures"
rm -rf "$BASE"
mkdir -p "$BASE"

# ---------- fixture 1: secrets-precommit ----------
F1="$BASE/apilog"
mkdir -p "$F1/src"
cat > "$F1/package.json" <<'EOF'
{
  "name": "apilog",
  "version": "0.3.1",
  "private": true,
  "scripts": {
    "start": "node src/server.js",
    "lint": "eslint src",
    "test": "node --test"
  }
}
EOF
cat > "$F1/src/server.js" <<'EOF'
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
EOF
cat > "$F1/src/config.js" <<'EOF'
function loadConfig() {
  return {
    port: Number(process.env.PORT || 3010),
    stripeKey: process.env.STRIPE_SECRET_KEY,
    dbUrl: process.env.DATABASE_URL,
  };
}

module.exports = { loadConfig };
EOF
cat > "$F1/.env" <<'EOF'
PORT=3010
STRIPE_SECRET_KEY=sk_live_PLACEHOLDER_NOT_A_REAL_KEY_000000
DATABASE_URL=postgres://apilog:PLACEHOLDER_PW@localhost:5432/apilog
EOF
cat > "$F1/.env.example" <<'EOF'
PORT=3010
STRIPE_SECRET_KEY=
DATABASE_URL=
EOF
cat > "$F1/.gitignore" <<'EOF'
node_modules/
*.log
EOF
cat > "$F1/README.md" <<'EOF'
# apilog

内部 API 日志服务。

## 跑起来
    cp .env.example .env   # 填上 key
    npm start

## 部署
Fly.io，`fly deploy`。环境变量在 fly secrets 里。
EOF
(cd "$F1" && git init -q && git add -A && git -c user.email=dev@local -c user.name=dev commit -qm "init apilog")

# ---------- fixture 2: coverage-gate ----------
F2="$BASE/pricecalc"
mkdir -p "$F2/src" "$F2/test" "$F2/.github/workflows"
cat > "$F2/package.json" <<'EOF'
{
  "name": "pricecalc",
  "version": "1.2.0",
  "private": true,
  "scripts": {
    "lint": "eslint src || true",
    "test": "node --test",
    "coverage": "node --experimental-test-coverage --test"
  }
}
EOF
cat > "$F2/src/price.js" <<'EOF'
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
EOF
cat > "$F2/test/price.test.js" <<'EOF'
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
EOF
cat > "$F2/.github/workflows/ci.yml" <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test
EOF
cat > "$F2/README.md" <<'EOF'
# pricecalc

定价计算库，被结算服务依赖。

## 开发
    npm test
    npm run coverage
EOF
(cd "$F2" && git init -q && git add -A && git -c user.email=dev@local -c user.name=dev commit -qm "init pricecalc")

echo "fixtures ready: $BASE"
