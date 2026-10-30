import { Link } from 'react-router-dom';

export default function Brand({ footer = false }) {
  return (
    <Link className={`brand ${footer ? 'brand-footer' : ''}`} to="/" aria-label="اووِل، صفحه نخست">
      <span className="brand-word" dir="ltr" lang="en">owel<span>.</span></span>
      <span className="brand-caption">اووِل</span>
    </Link>
  );
}
