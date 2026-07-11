const { listItems } = require('./handlers/items');

// 路由表：pathname → handler
const routes = {
  '/items': listItems,
};

module.exports = { routes };
