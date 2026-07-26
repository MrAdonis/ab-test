// 登录失败锁定：借用 SESSIONS 这个 KV 命名空间存计数，按邮箱维度限流，
// 防止对已知邮箱做密码撞库/暴力枚举。

const MAX_ATTEMPTS = 5;
const LOCK_SECONDS = 15 * 60;
const WINDOW_SECONDS = 15 * 60;

interface AttemptState {
  count: number;
  lockedUntil?: number;
}

function attemptKey(email: string): string {
  return `login_attempt:${email}`;
}

async function readState(kv: KVNamespace, email: string): Promise<AttemptState> {
  const raw = await kv.get(attemptKey(email));
  return raw ? (JSON.parse(raw) as AttemptState) : { count: 0 };
}

/** 返回 null 表示未锁定，否则返回还需等待的秒数。 */
export async function isLocked(kv: KVNamespace, email: string): Promise<number | null> {
  const state = await readState(kv, email);
  if (state.lockedUntil && state.lockedUntil > Date.now()) {
    return Math.ceil((state.lockedUntil - Date.now()) / 1000);
  }
  return null;
}

export async function recordAttempt(kv: KVNamespace, email: string, success: boolean): Promise<void> {
  if (success) {
    await kv.delete(attemptKey(email));
    return;
  }
  const state = await readState(kv, email);
  state.count += 1;
  if (state.count >= MAX_ATTEMPTS) {
    state.lockedUntil = Date.now() + LOCK_SECONDS * 1000;
    await kv.put(attemptKey(email), JSON.stringify(state), { expirationTtl: LOCK_SECONDS });
  } else {
    await kv.put(attemptKey(email), JSON.stringify(state), { expirationTtl: WINDOW_SECONDS });
  }
}
