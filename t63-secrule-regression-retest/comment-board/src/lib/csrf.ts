// 基础的跨站请求防护：比对 Origin（或 Referer 兜底）与当前请求的 host，
// 挡掉第三方页面自动提交表单/fetch 到本站状态变更接口的情况。
export function isSameOrigin(request: Request): boolean {
  const origin = request.headers.get('origin');
  if (!origin) {
    const referer = request.headers.get('referer');
    if (!referer) return true;
    try {
      return new URL(referer).origin === new URL(request.url).origin;
    } catch {
      return false;
    }
  }
  try {
    return new URL(origin).origin === new URL(request.url).origin;
  } catch {
    return false;
  }
}
