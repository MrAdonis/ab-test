/// <reference types="astro/client" />

interface Env {
  DB: D1Database;
  SESSIONS: KVNamespace;
}

type Runtime = import('@astrojs/cloudflare').Runtime<Env>;

declare namespace App {
  interface Locals extends Runtime {}
}
