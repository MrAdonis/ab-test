import type { APIRoute } from 'astro';
import { isSameOrigin } from '../../lib/csrf';
import { verifyPassword } from '../../lib/password';
import { createSession, SESSION_COOKIE, SESSION_TTL_SECONDS } from '../../lib/session';
import { isLocked, recordAttempt } from '../../lib/rateLimit';

export const prerender = false;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const EMAIL_MAX = 254;
const PASSWORD_MAX = 256;

// 账号不存在时用的哈希参数，保证“查不到用户”和“密码算错”两条路径耗时一致，
// 避免通过响应时间枚举已注册邮箱。
const DUMMY_SALT = '00'.repeat(16);
const DUMMY_HASH = '00'.repeat(32);
const DUMMY_ITERATIONS = 120_000;

interface UserRow {
  id: string;
  email: string;
  password_hash: string;
  password_salt: string;
  password_iterations: number;
}

export const POST: APIRoute = async ({ request, locals, cookies }) => {
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

  if (!email || email.length > EMAIL_MAX || !EMAIL_RE.test(email) || !password || password.length > PASSWORD_MAX) {
    // 故意用同一句模糊错误，不区分“邮箱不存在”和“密码不对”，防止用户枚举。
    return json({ error: '邮箱或密码错误' }, 400);
  }

  const sessions = locals.runtime.env.SESSIONS;

  const retryAfter = await isLocked(sessions, email);
  if (retryAfter !== null) {
    return json({ error: '尝试次数过多，请稍后再试' }, 429, { 'Retry-After': String(retryAfter) });
  }

  const db = locals.runtime.env.DB;
  const user = await db
    .prepare('SELECT id, email, password_hash, password_salt, password_iterations FROM users WHERE email = ?')
    .bind(email)
    .first<UserRow>();

  const valid = user
    ? await verifyPassword(password, user.password_salt, user.password_hash, user.password_iterations)
    : await verifyPassword(password, DUMMY_SALT, DUMMY_HASH, DUMMY_ITERATIONS);

  await recordAttempt(sessions, email, Boolean(user) && valid);

  if (!user || !valid) {
    return json({ error: '邮箱或密码错误' }, 401);
  }

  const sessionId = await createSession(sessions, user.id, user.email);
  cookies.set(SESSION_COOKIE, sessionId, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: SESSION_TTL_SECONDS,
  });

  return json({ ok: true, email: user.email });
};

function json(data: unknown, status = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers },
  });
}
