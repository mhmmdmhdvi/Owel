import { useRef, useState } from 'react';
import Icon from '../../components/ui/Icon.jsx';
import FormField from './FormField.jsx';
import { submitReservation } from './api.js';

export default function ReservationForm({ onSuccess }) {
  const [values, setValues] = useState({ full_name: '', email: '', whatsapp: '' });
  const [fields, setFields] = useState({});
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const inFlight = useRef(false);
  const alertRef = useRef(null);

  function update(event) {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
    setFields((current) => ({ ...current, [name]: undefined }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (inFlight.current) return;
    inFlight.current = true;
    setSubmitting(true);
    setError('');
    setFields({});
    try {
      await submitReservation(values);
      onSuccess();
    } catch (failure) {
      setError(failure.message);
      setFields(failure.fields || {});
      requestAnimationFrame(() => alertRef.current?.focus());
    } finally {
      inFlight.current = false;
      setSubmitting(false);
    }
  }

  return (
    <form className="reservation-form" onSubmit={handleSubmit} aria-busy={submitting}>
      {error && <p className="reservation-alert" role="alert" tabIndex={-1} ref={alertRef}>{error}</p>}
      <fieldset disabled={submitting}>
        <legend className="sr-only">مشخصات تماس</legend>
        <FormField name="full_name" label="نام و نام خانوادگی" autoComplete="name" maxLength={120} value={values.full_name} onChange={update} error={fields.full_name} />
        <FormField name="email" label="ایمیل" type="email" dir="ltr" autoComplete="email" maxLength={254} placeholder="name@example.com" value={values.email} onChange={update} error={fields.email} />
        <FormField name="whatsapp" label="شماره واتس‌اپ" type="tel" dir="ltr" autoComplete="tel" maxLength={40} placeholder="+1 202 555 0123" hint="شماره را همراه کد کشور وارد کنید." value={values.whatsapp} onChange={update} error={fields.whatsapp} />
        <button className="button-primary reservation-submit" type="submit">{submitting ? 'در حال ارسال…' : 'ثبت درخواست'}<Icon name="left" /></button>
      </fieldset>
    </form>
  );
}
