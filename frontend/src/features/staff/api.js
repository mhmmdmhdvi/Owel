export class StaffError extends Error {
  constructor(message, status = 0, retryAfter = 0) {
    super(message);
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

export async function staffRequest(endpoint, { token, method = 'GET', body, signal } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body) headers['Content-Type'] = 'application/json';
  let response;
  try {
    response = await fetch(`/api/staff/${endpoint}`, { method, headers, credentials: 'omit', body: body ? JSON.stringify(body) : undefined, signal });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new StaffError('ارتباط برقرار نشد. دوباره تلاش کنید.');
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof data?.detail === 'string' ? data.detail : 'درخواست انجام نشد. دوباره تلاش کنید.';
    throw new StaffError(detail, response.status, Number(data?.retry_after || response.headers.get('Retry-After') || 0));
  }
  return data;
}

export function telegramInitData() {
  return window.Telegram?.WebApp?.initData || new URLSearchParams(window.location.hash.slice(1)).get('tgWebAppData') || '';
}
