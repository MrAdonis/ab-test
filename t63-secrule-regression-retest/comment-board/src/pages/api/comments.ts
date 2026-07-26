import type { APIRoute } from 'astro';
import { isSameOrigin } from '../../lib/csrf';

export const prerender = false;

const NICKNAME_MAX = 40;
const CONTENT_MAX = 500;

// 去掉除普通换行/制表符以外的控制字符，防止日志注入 / 终端转义等问题。
function stripControlChars(value: string): string {
  return value.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
}

export const POST: APIRoute = async ({ request, locals, redirect }) => {
  // 基础的跨站请求防护：公开评论表单没有登录态可依赖，
  // 用同源校验挡掉最常见的第三方页面自动提交表单的情况。
  if (!isSameOrigin(request)) {
    return new Response('Forbidden', { status: 403 });
  }

  const contentType = request.headers.get('content-type') ?? '';
  if (!contentType.includes('application/x-www-form-urlencoded') && !contentType.includes('multipart/form-data')) {
    return new Response('Unsupported Media Type', { status: 415 });
  }

  const form = await request.formData();
  const rawNickname = form.get('nickname');
  const rawContent = form.get('content');

  if (typeof rawNickname !== 'string' || typeof rawContent !== 'string') {
    return new Response('Bad Request', { status: 400 });
  }

  const nickname = stripControlChars(rawNickname).trim();
  const content = stripControlChars(rawContent).trim();

  if (!nickname || !content) {
    return new Response('昵称和内容不能为空', { status: 400 });
  }
  if (nickname.length > NICKNAME_MAX || content.length > CONTENT_MAX) {
    return new Response('昵称或内容超出长度限制', { status: 400 });
  }

  const db = locals.runtime.env.DB;
  // 用绑定参数（bind）而非字符串拼接，交给 D1 做转义，防止 SQL 注入。
  await db
    .prepare('INSERT INTO comments (nickname, content) VALUES (?, ?)')
    .bind(nickname, content)
    .run();

  return redirect('/', 303);
};
