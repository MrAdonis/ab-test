§3 安全边界已加载，结论如下。
§3 是 HARD-GATE：Chrome 已登录已开（用户确认）。动手前必须告知：agent 接管后能访问当前 profile 全部数据（所有 tabs/cookies/localStorage/sessionStorage/JS-API），含 Stripe/CF/Shopify/飞书/X 等一切已登录服务，不只订单页。只在信任 prompt 流程开，用完 revert（去 --autoConnect），不在开启时跑陌生站点。第一步是告知+请用户确认两件事（接受范围 / 用完去掉 --autoConnect），确认后用 list_pages 定位再逐屏抓。
