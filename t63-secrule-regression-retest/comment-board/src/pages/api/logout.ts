import type { APIRoute } from 'astro';
import { isSameOrigin } from '../../lib/csrf';
import { destroySession, SESSION_COOKIE } from '../../lib/session';

export const prerender = false;

export const POST: APIRoute = async ({ request, locals, cookies }) => {
  if (!isSameOrigin(request)) {
    return json({ error: 'Forbidden' }, 403);
  }

  const sessionId = cookies.get(SESSION_COOKIE)?.value;
  if (sessionId) {
    await destroySession(locals.runtime.env.SESSIONS, sessionId);
  }
  cookies.delete(SESSION_COOKIE, { path: '/' });

  return json({ ok: true });
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
}
