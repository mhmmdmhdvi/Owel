import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import ReservationForm from './ReservationForm.jsx';
import ReservationSuccess from './ReservationSuccess.jsx';
import './reservation.css';

export default function ReservationPage() {
  const [submitted, setSubmitted] = useState(false);
  useEffect(() => {
    const original = document.title;
    document.title = 'درخواست رزرو جلسه | اووِل';
    return () => { document.title = original; };
  }, []);

  return (
    <div className="page-shell reservation-page">
      {submitted ? <ReservationSuccess /> : (
        <div className="reservation-layout">
          <div className="reservation-intro">
            <Link className="eyebrow" to="/">صفحه نخست</Link>
            <h1>درخواست رزرو جلسه</h1>
            <p>مشاوره آنلاین فردی</p>
            <div className="reservation-session-note">جلسه ۵۰ دقیقه‌ای در بستر Google Meet</div>
          </div>
          <ReservationForm onSuccess={() => setSubmitted(true)} />
        </div>
      )}
    </div>
  );
}
