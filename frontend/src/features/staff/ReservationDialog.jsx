import { useEffect, useRef, useState } from 'react';
import Icon from '../../components/ui/Icon.jsx';
import { staffRequest } from './api.js';

export default function ReservationDialog({ id, token, canChange, onClose, onSaved, onExpired }) {
  const dialog = useRef(null);
  const [record, setRecord] = useState(null);
  const [handled, setHandled] = useState(false);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const element = dialog.current;
    element.showModal();
    return () => element.close();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    staffRequest(`reservations/${id}/`, { token, signal: controller.signal }).then((data) => {
      setRecord(data); setHandled(data.handled); setNotes(data.admin_notes);
    }).catch((failure) => {
      if (failure.name === 'AbortError') return;
      if ([401, 403].includes(failure.status)) onExpired(failure.message);
      else setError(failure.message);
    });
    return () => controller.abort();
  }, [id, token, onExpired]);

  async function save(event) {
    event.preventDefault();
    if (saving) return;
    setSaving(true); setError('');
    try {
      await staffRequest(`reservations/${id}/`, { token, method: 'PATCH', body: { handled, admin_notes: notes } });
      onSaved();
    } catch (failure) {
      if ([401, 403].includes(failure.status)) onExpired(failure.message);
      else setError(failure.message);
    } finally { setSaving(false); }
  }

  return (
    <dialog className="staff-dialog" ref={dialog} aria-labelledby="detail-title" onCancel={(event) => { event.preventDefault(); onClose(); }}>
      <div className="staff-dialog-heading"><h2 id="detail-title">جزئیات درخواست</h2><button className="staff-icon-button" type="button" aria-label="بستن" onClick={onClose}><Icon name="close" /></button></div>
      {error && <p className="staff-alert" role="alert">{error}</p>}
      {!record ? !error && <p role="status">در حال بارگذاری…</p> : <>
        <dl className="staff-contact-details"><div><dt>نام</dt><dd>{record.full_name}</dd></div><div><dt>ایمیل</dt><dd><a href={`mailto:${record.email}`}><bdi>{record.email}</bdi></a></dd></div><div><dt>واتس‌اپ</dt><dd><a href={`https://wa.me/${record.whatsapp.slice(1)}`} target="_blank" rel="noopener noreferrer"><bdi>{record.whatsapp}</bdi></a></dd></div></dl>
        <form onSubmit={save}>
          <label className="staff-check"><input type="checkbox" checked={handled} disabled={!canChange || saving} onChange={(event) => setHandled(event.target.checked)} />بررسی شده</label>
          <label className="staff-notes-label" htmlFor="staff-notes">یادداشت داخلی</label>
          <textarea id="staff-notes" maxLength={2000} rows={4} disabled={!canChange || saving} value={notes} onChange={(event) => setNotes(event.target.value)} />
          {canChange && <button className="button-primary" type="submit" disabled={saving}>{saving ? 'در حال ذخیره…' : 'ذخیره'}</button>}
        </form>
      </>}
    </dialog>
  );
}
