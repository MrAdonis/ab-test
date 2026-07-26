import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

// D1 只能在 Cloudflare 运行时里访问，所以整站用 server 输出（SSR），
// 由 @astrojs/cloudflare adapter 提供 Astro.locals.runtime.env.DB 绑定。
export default defineConfig({
  output: 'server',
  adapter: cloudflare({
    platformProxy: {
      enabled: true, // 本地 `astro dev` 时通过 wrangler 代理模拟 D1 绑定
    },
  }),
});
