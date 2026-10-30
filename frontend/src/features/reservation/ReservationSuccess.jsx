import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon.jsx';

export default function ReservationSuccess() {
  const heading = useRef(null);
  useEffect(() => { heading.current?.focus(); }, []);
  return (
    <section className="reservation-success">
      <span className="reservation-success-mark" aria-hidden="true">✓</span>
      <h1 ref={heading} tabIndex={-1}>درخواست شما ثبت شد.</h1>
      <Link className="text-link" to="/">بازگشت به صفحه نخست<Icon name="left" /></Link>
    </section>
  );
}
