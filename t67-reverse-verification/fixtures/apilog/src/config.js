function loadConfig() {
  return {
    port: Number(process.env.PORT || 3010),
    stripeKey: process.env.STRIPE_SECRET_KEY,
    dbUrl: process.env.DATABASE_URL,
  };
}

module.exports = { loadConfig };
