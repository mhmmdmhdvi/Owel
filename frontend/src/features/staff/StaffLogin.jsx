import { useEffect, useRef, useState } from 'react';
import { staffRequest, telegramInitData } from './api.js';

export default function StaffLogin({ onLogin, notice }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(notice || '');
  const [busy, setBusy] = useState(false);
  const [lockedUntil, setLockedUntil] = useState(0);
  const [remaining, setRemaining] = useState(0);
  const inFlight = useRef(false);
  const alert = useRef(null);

  useEffect(() => { setError(notice || ''); }, [notice]);

  useEffect(() => {
    if (!lockedUntil) { setRemaining(0); return; }
    const update = () => setRemaining(Math.max(0, Math.ceil((lockedUntil - Date.now()) / 1000)));
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, [lockedUntil]);

  async function submit(event) {
    event.preventDefault();
    if (inFlight.current || remaining > 0) return;
    inFlight.current = true;
    setBusy(true);
    setError('');
    try {
      const session = await staffRequest('login/', { method: 'POST', body: { username, password, telegram_init_data: telegramInitData() } });
      setPassword('');
      onLogin(session);
    } catch (failure) {
      setPassword('');
      setError(failure.message);
      if (failure.retryAfter) setLockedUntil(Date.now() + failure.retryAfter * 1000);
      requestAnimationFrame(() => alert.current?.focus());
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  return (
    <section className="staff-login" aria-labelledby="staff-login-title">
      <span className="eyebrow">پنل مدیریت</span>
      <h1 id="staff-login-title">ورود به حساب</h1>
      <form onSubmit={submit}>
        {error && <p role="alert" className="staff-alert" tabIndex={-1} ref={alert}>{error}</p>}
        {remaining > 0 && <p className="staff-lock-time" role="timer">زمان باقی‌مانده: {Math.floor(remaining / 60).toString().padStart(2, '0')}:{(remaining % 60).toString().padStart(2, '0')}</p>}
        <label htmlFor="staff-username">نام کاربری</label>
        <input id="staff-username" dir="ltr" autoComplete="username" required maxLength={150} value={username} disabled={busy} onChange={(event) => { setUsername(event.target.value); setLockedUntil(0); }} />
        <label htmlFor="staff-password">رمز عبور</label>
        <input id="staff-password" type="password" dir="ltr" autoComplete="current-password" required maxLength={1024} value={password} disabled={busy || remaining > 0} onChange={(event) => setPassword(event.target.value)} />
        <button className="button-primary staff-login-submit" disabled={busy || remaining > 0} type="submit">{busy ? 'در حال ورود…' : 'ورود'}</button>
      </form>
    </section>
  );
}
