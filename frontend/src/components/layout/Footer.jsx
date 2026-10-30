import Brand from '../ui/Brand.jsx';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="page-shell">
        <div className="footer-main flex flex-wrap items-center justify-between gap-8">
          <div className="flex items-center gap-6"><Brand footer /><span className="footer-description">روانشناسی کل‌نگر و مایندفولنس</span></div>
        </div>
        <div className="footer-bottom flex flex-wrap items-center justify-between gap-4">
          <span>© کلیه حقوق مادی و معنوی برای وب‌سایت Owel (اووِل) محفوظ است.</span>
          <nav aria-label="پیوندهای پایین صفحه" className="flex flex-wrap gap-x-7"><Link to="/#classes">کلاس‌های آموزشی</Link><Link to="/#retreat">سفرهای «حضور در هستی»</Link><Link to="/#about">درباره Owel</Link><Link to="/#podcast">پادکست و یوتیوب</Link></nav>
          <span className="footer-word" lang="en" dir="ltr">OWEL</span>
        </div>
      </div>
    </footer>
  );
}
