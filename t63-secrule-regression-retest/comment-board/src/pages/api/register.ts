import type { APIRoute } from 'astro';
import { isSameOrigin } from '../../lib/csrf';
import { hashPassword } from '../../lib/password';

// 演示/建号用途：真实产品里注册通常还需要邮箱验证、验证码等额外防护，
// 这里只覆盖“建一个能登录的账号”这个最小需求。

export const prerender = false;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const EMAIL_MAX = 254;
const PASSWORD_MIN = 8;
const PASSWORD_MAX = 256;

export const POST: APIRoute = async ({ request, locals }) => {
  if (!isSameOrigin(request)) {
    return json({ error: 'Forbidden' }, 403);
  }

  let body: { email?: unknown; password?: unknown };
  try {
    body = await request.json();
  } catch {
    return json({ error: '请求体必须是 JSON' }, 400);
  }

  const email = String(body.email ?? '').trim().toLowerCase();
  const password = String(body.password ?? '');

  if (!email || email.length > EMAIL_MAX || !EMAIL_RE.test(email)) {
    return json({ error: '邮箱格式不正确' }, 400);
  }
  if (password.length < PASSWORD_MIN || password.length > PASSWORD_MAX) {
    return json({ error: `密码长度需在 ${PASSWORD_MIN}-${PASSWORD_MAX} 位之间` }, 400);
  }

  const db = locals.runtime.env.DB;
  const existing = await db.prepare('SELECT id FROM users WHERE email = ?').bind(email).first();
  if (existing) {
    return json({ error: '该邮箱已注册' }, 409);
  }

  const { hash, salt, iterations } = await hashPassword(password);
  const id = crypto.randomUUID();
  await db
    .prepare(
      'INSERT INTO users (id, email, password_hash, password_salt, password_iterations, created_at) VALUES (?, ?, ?, ?, ?, ?)',
    )
    .bind(id, email, hash, salt, iterations, Date.now())
    .run();

  return json({ ok: true });
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
}
