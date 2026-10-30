import { lazy, Suspense } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import Header from './components/layout/Header.jsx';
import Footer from './components/layout/Footer.jsx';
import HomePage from './features/home/HomePage.jsx';
import BackToTop from './components/ui/BackToTop.jsx';
import ScrollToPage from './components/layout/ScrollToPage.jsx';

const ReservationPage = lazy(() => import('./features/reservation/ReservationPage.jsx'));
const StaffPage = lazy(() => import('./features/staff/StaffPage.jsx'));

export default function App() {
  const staffPage = useLocation().pathname === '/staff';
  return (
    <>
      <a className="skip-link" href="#main">رفتن به محتوای اصلی</a>
      {!staffPage && <Header />}
      <ScrollToPage />
      <main id="main">
        <Suspense fallback={<div className="page-shell route-loading" role="status">در حال بارگذاری…</div>}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/reservation" element={<ReservationPage />} />
            <Route path="/staff" element={<StaffPage />} />
            <Route path="*" element={<section className="page-shell route-loading"><h1>صفحه پیدا نشد.</h1><Link className="text-link" to="/">صفحه نخست</Link></section>} />
          </Routes>
        </Suspense>
      </main>
      {!staffPage && <><Footer /><BackToTop /></>}
    </>
  );
}
