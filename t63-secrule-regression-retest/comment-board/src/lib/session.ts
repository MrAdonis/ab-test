import type { AstroCookies } from 'astro';

export const SESSION_COOKIE = 'session_id';
export const SESSION_TTL_SECONDS = 60 * 60 * 24; // 24 小时

export interface SessionData {
  userId: string;
  email: string;
  createdAt: number;
}

export async function createSession(sessions: KVNamespace, userId: string, email: string): Promise<string> {
  const sessionId = generateSessionId();
  const data: SessionData = { userId, email, createdAt: Date.now() };
  // expirationTtl 让 KV 到期自动清理，服务端会话生命周期与 Cookie Max-Age 保持一致。
  await sessions.put(`session:${sessionId}`, JSON.stringify(data), { expirationTtl: SESSION_TTL_SECONDS });
  return sessionId;
}

export async function getSession(sessions: KVNamespace, sessionId: string): Promise<SessionData | null> {
  const raw = await sessions.get(`session:${sessionId}`);
  return raw ? (JSON.parse(raw) as SessionData) : null;
}

export async function destroySession(sessions: KVNamespace, sessionId: string): Promise<void> {
  await sessions.delete(`session:${sessionId}`);
}

/** 供受保护接口复用：从请求 Cookie 里取 session，无效/过期统一返回 null。 */
export async function requireSession(
  cookies: AstroCookies,
  sessions: KVNamespace,
): Promise<SessionData | null> {
  const sessionId = cookies.get(SESSION_COOKIE)?.value;
  if (!sessionId) return null;
  return getSession(sessions, sessionId);
}

function generateSessionId(): string {
  // 256 bit 随机数，仅作为 KV 查找用的不透明 token：
  // 没有对应 KV 记录就无法通过校验，无需再额外签名/加密。
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}
