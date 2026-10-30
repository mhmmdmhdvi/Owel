import { useCallback, useEffect, useRef, useState } from 'react';
import Brand from '../../components/ui/Brand.jsx';
import StaffLogin from './StaffLogin.jsx';
import ReservationTable from './ReservationTable.jsx';
import { staffRequest } from './api.js';
import './staff.css';

export default function StaffPage() {
  // Session tokens deliberately stay in memory and disappear on page refresh.
  const [session, setSession] = useState(null);
  const [notice, setNotice] = useState('');
  const sessionVersion = useRef(0);
  useEffect(() => {
    const title = document.title;
    document.title = 'پنل مدیریت | اووِل';
    return () => { document.title = title; };
  }, []);
  const expire = useCallback((message) => { sessionVersion.current += 1; setSession(null); setNotice(message || 'لطفاً دوباره وارد شوید.'); }, []);

  async function logout() {
    const token = session?.token;
    if (!token) return;
    const version = ++sessionVersion.current;
    // Clear contacts and the in-memory token before waiting for the network.
    setSession(null); setNotice('');
    try {
      await staffRequest('logout/', { token, method: 'POST' });
    } catch (error) {
      if (error.status !== 401 && sessionVersion.current === version) {
        setNotice('از این دستگاه خارج شدید؛ پایان نشست سرور تأیید نشد.');
      }
    }
  }

  return (
    <div className="staff-page">
      <header className="staff-header"><div className="page-shell"><Brand />{session && <div className="staff-account"><span>{session.user.username}</span><button className="staff-secondary" type="button" onClick={logout}>خروج</button></div>}</div></header>
      <div className="page-shell staff-content">
        {session ? <>
          <div className="staff-connection"><span className={session.user.telegram_connected ? 'connected' : ''}>{session.user.telegram_connected ? 'اعلان تلگرام فعال است' : 'حساب تلگرام متصل نیست'}</span></div>
          {notice && <p className="staff-alert" role="alert">{notice}</p>}
          <ReservationTable session={session} onExpired={expire} />
        </> : <StaffLogin notice={notice} onLogin={(value) => { sessionVersion.current += 1; setSession(value); setNotice(''); }} />}
      </div>
    </div>
  );
}
