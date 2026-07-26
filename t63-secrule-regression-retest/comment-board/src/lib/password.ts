// PBKDF2-SHA256 口令哈希。Workers 运行时只有 Web Crypto（无 bcrypt/argon2 原生实现），
// PBKDF2 是唯一的内建选项；迭代次数需要在“抗暴力破解”和“Workers CPU 时间预算”之间取舍，
// 这里取 120,000（Bundled 用量模型下单次约几十毫秒）。若部署在 Unbound 用量模型，
// 可以调大到 OWASP 建议的 600,000。
const ITERATIONS = 120_000;

export interface PasswordHash {
  hash: string;
  salt: string;
  iterations: number;
}

export async function hashPassword(password: string): Promise<PasswordHash> {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const bits = await deriveBits(password, salt, ITERATIONS);
  return { hash: toHex(bits), salt: toHex(salt), iterations: ITERATIONS };
}

export async function verifyPassword(
  password: string,
  saltHex: string,
  hashHex: string,
  iterations: number,
): Promise<boolean> {
  const salt = fromHex(saltHex);
  const computed = await deriveBits(password, salt, iterations);
  return constantTimeEqual(computed, fromHex(hashHex));
}

async function deriveBits(password: string, salt: Uint8Array, iterations: number): Promise<Uint8Array> {
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(password),
    'PBKDF2',
    false,
    ['deriveBits'],
  );
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt, iterations, hash: 'SHA-256' }, keyMaterial, 256);
  return new Uint8Array(bits);
}

function toHex(bytes: Uint8Array): string {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

function fromHex(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}

// 按位异或累加、不提前 return，避免比较耗时随首个不匹配字节而变化（时序旁道防护）。
function constantTimeEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a[i] ^ b[i];
  }
  return diff === 0;
}
