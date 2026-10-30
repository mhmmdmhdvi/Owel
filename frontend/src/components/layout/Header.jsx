import { useEffect, useRef, useState } from 'react';
import Brand from '../ui/Brand.jsx';
import Icon from '../ui/Icon.jsx';
import { Link } from 'react-router-dom';

const links = [
  { href: '#home', label: 'صفحه نخست' },
  { href: '#services', label: 'خدمات' },
  { href: '#approach', label: 'رویکرد درمانی' },
  { href: '#classes', label: 'کلاس‌های آموزشی' },
  { href: '#retreat', label: 'حضور در هستی' },
  { href: '#about', label: 'درباره Owel' },
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const toggleRef = useRef(null);

  useEffect(() => {
    if (!menuOpen) return;
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') {
        setMenuOpen(false);
        toggleRef.current?.focus();
      }
    };
    const breakpoint = window.matchMedia('(min-width: 1024px)');
    const closeOnDesktop = () => { if (breakpoint.matches) setMenuOpen(false); };
    document.addEventListener('keydown', closeOnEscape);
    breakpoint.addEventListener('change', closeOnDesktop);
    return () => {
      document.removeEventListener('keydown', closeOnEscape);
      breakpoint.removeEventListener('change', closeOnDesktop);
    };
  }, [menuOpen]);

  return (
    <header className="site-header">
      <div className="page-shell header-inner">
        <Brand />
        <nav id="main-navigation" aria-label="فهرست اصلی" className={`main-navigation ${menuOpen ? 'is-open' : ''}`}>
          {links.map(({ href, label }) => (
            <Link key={href} to={`/${href}`} onClick={() => setMenuOpen(false)}>{label}</Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Link className="header-cta" to="/reservation" onClick={() => setMenuOpen(false)}>رزرو وقت آنلاین <Icon name="arrow" /></Link>
          <button ref={toggleRef} className="menu-toggle" type="button" aria-label="فهرست" aria-expanded={menuOpen} aria-controls="main-navigation" onClick={() => setMenuOpen(!menuOpen)}>
            <Icon name={menuOpen ? 'close' : 'menu'} />
          </button>
        </div>
      </div>
    </header>
  );
}
