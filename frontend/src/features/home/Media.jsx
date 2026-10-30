import { media } from './additionalContent.js';
import MediaCard from './MediaCard.jsx';

export default function Media() {
  return (
    <section id="podcast" className="media-section content-section" aria-labelledby="media-title">
      <div className="page-shell">
        <div className="content-heading"><span className="eyebrow">{media.eyebrow}</span><h2 id="media-title">{media.title}</h2><p>{media.description}</p></div>
        <div className="media-grid">{media.items.map((item) => <MediaCard key={item.title} item={item} />)}</div>
      </div>
    </section>
  );
}
