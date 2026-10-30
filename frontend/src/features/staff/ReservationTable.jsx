import { useEffect, useState } from 'react';
import ReservationDialog from './ReservationDialog.jsx';
import { staffRequest } from './api.js';

const dateFormat = new Intl.DateTimeFormat('fa-IR', { dateStyle: 'medium', timeStyle: 'short' });
const numbers = new Intl.NumberFormat('fa-IR');

export default function ReservationTable({ session, onExpired }) {
  const [search, setSearch] = useState('');
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');
  const [page, setPage] = useState(1);
  const [refresh, setRefresh] = useState(0);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError('');
    const params = new URLSearchParams({ q: query, status, page: String(page) });
    staffRequest(`reservations/?${params}`, { token: session.token, signal: controller.signal }).then(setData).catch((failure) => {
      if (failure.name === 'AbortError') return;
      if ([401, 403].includes(failure.status)) onExpired(failure.message);
      else setError(failure.message);
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [session.token, query, status, page, refresh, onExpired]);

  return (
    <section aria-labelledby="staff-reservations-title">
      <div className="staff-title-row"><div><span className="eyebrow">پنل مدیریت</span><h1 id="staff-reservations-title">درخواست‌های رزرو</h1></div>{data && <span className="staff-result-count">{numbers.format(data.count)} درخواست</span>}</div>
      <form className="staff-toolbar" onSubmit={(event) => { event.preventDefault(); setPage(1); setQuery(search.trim()); setRefresh((current) => current + 1); }}>
        <div className="staff-search"><label className="sr-only" htmlFor="staff-search">جست‌وجو</label><input id="staff-search" placeholder="نام، ایمیل یا شماره واتس‌اپ" maxLength={200} value={search} onChange={(event) => setSearch(event.target.value)} /><button type="submit" className="staff-secondary">جست‌وجو</button></div>
        <div><label className="sr-only" htmlFor="staff-status">وضعیت</label><select id="staff-status" value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }}><option value="all">همه درخواست‌ها</option><option value="new">بررسی نشده</option><option value="handled">بررسی شده</option></select></div>
      </form>
      {error && <p className="staff-alert" role="alert">{error}<button className="text-link" type="button" onClick={() => setRefresh((current) => current + 1)}>تلاش مجدد</button></p>}
      {loading && <p className="staff-loading" role="status">در حال بارگذاری…</p>}
      {data && <div className="staff-table-wrap" aria-busy={loading}>
        <table className="staff-table"><caption className="sr-only">درخواست‌های رزرو</caption><thead><tr><th scope="col">نام و اطلاعات تماس</th><th scope="col">واتس‌اپ</th><th scope="col">زمان ثبت</th><th scope="col">وضعیت</th><th scope="col">جزئیات</th></tr></thead>
          <tbody>{data.results.map((record) => <tr key={record.id}>
            <td className="staff-name-cell"><strong>{record.full_name}</strong><span><bdi>{record.email}</bdi></span></td>
            <td data-label="واتس‌اپ"><bdi>{record.whatsapp}</bdi></td><td data-label="زمان ثبت">{dateFormat.format(new Date(record.created_at))}</td>
            <td data-label="وضعیت"><span className={`staff-status ${record.handled ? 'is-handled' : ''}`}>{record.handled ? 'بررسی شده' : 'بررسی نشده'}</span></td>
            <td><button className="staff-secondary" type="button" onClick={() => setSelected(record.id)}>جزئیات</button></td>
          </tr>)}</tbody>
        </table>
        {!data.results.length && <p className="staff-empty">درخواستی پیدا نشد.</p>}
      </div>}
      {data && data.pages > 1 && <nav className="staff-pagination" aria-label="صفحه‌بندی"><button className="staff-secondary" disabled={page <= 1 || loading} onClick={() => setPage((current) => current - 1)}>قبلی</button><span>{numbers.format(data.page)} از {numbers.format(data.pages)}</span><button className="staff-secondary" disabled={page >= data.pages || loading} onClick={() => setPage((current) => current + 1)}>بعدی</button></nav>}
      {selected && <ReservationDialog key={selected} id={selected} token={session.token} canChange={data?.can_change} onExpired={onExpired} onClose={() => setSelected(null)} onSaved={() => { setSelected(null); setRefresh((current) => current + 1); }} />}
    </section>
  );
}
