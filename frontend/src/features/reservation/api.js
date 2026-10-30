export class ReservationError extends Error {
  constructor(message, fields = {}) {
    super(message);
    this.fields = fields;
  }
}

export async function submitReservation(values) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch('/api/reservations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values),
      signal: controller.signal,
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const fields = {};
      for (const field of ['full_name', 'email', 'whatsapp']) {
        const errors = data?.[field];
        if (Array.isArray(errors) && typeof errors[0] === 'string') fields[field] = errors[0];
      }
      throw new ReservationError(
        response.status === 429 ? 'تعداد درخواست‌ها زیاد است؛ چند دقیقه دیگر دوباره تلاش کنید.' : 'ثبت درخواست انجام نشد. لطفاً اطلاعات را بررسی و دوباره تلاش کنید.',
        fields,
      );
    }
    if (response.status !== 201 || typeof data?.message !== 'string') {
      throw new ReservationError('پاسخ دریافت‌شده معتبر نیست. لطفاً دوباره تلاش کنید.');
    }
    return data;
  } catch (error) {
    if (error instanceof ReservationError) throw error;
    throw new ReservationError('ارتباط برقرار نشد. لطفاً دوباره تلاش کنید.');
  } finally {
    clearTimeout(timeout);
  }
}
