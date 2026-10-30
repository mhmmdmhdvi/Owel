import Icon from '../../components/ui/Icon.jsx';
import { hero } from './content.js';
import { Link } from 'react-router-dom';

export default function Hero() {
  return (
    <section id="home" className="hero" aria-labelledby="hero-title">
      <img
        className="hero-image"
        src="/images/landscape-1920.webp"
        srcSet="/images/landscape-640.webp 640w, /images/landscape-1100.webp 1100w, /images/landscape-1920.webp 1920w"
        sizes="100vw"
        width="1920"
        height="1280"
        alt=""
        fetchPriority="high"
      />
      <div className="page-shell hero-inner">
        <div className="hero-copy">
          <p className="hero-eyebrow">{hero.eyebrow}</p>
          <h1 id="hero-title">{hero.title}<br /><span>{hero.titleSecondLine}</span></h1>
          <p className="hero-description">{hero.description}</p>
          <div className="hero-actions flex flex-wrap items-center gap-x-7 gap-y-5">
            <Link className="button-primary" to="/reservation">{hero.primaryAction} <Icon name="left" /></Link>
            <a className="text-link" href="#retreats">{hero.secondaryAction} <Icon name="arrow" /></a>
          </div>
          <ul className="hero-notes">
            {hero.notes.map((note) => <li key={note}><span className="status-dot" />{note}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}
