import type { APIRoute } from 'astro';
import { requireSession } from '../../lib/session';

// 受保护接口示例：必须带有效 session cookie 才能访问。
export const prerender = false;

export const GET: APIRoute = async ({ locals, cookies }) => {
  const session = await requireSession(cookies, locals.runtime.env.SESSIONS);
  if (!session) {
    return json({ error: '未登录或会话已过期' }, 401);
  }
  return json({ email: session.email, loggedInSince: session.createdAt });
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
}
