import { retreat } from './additionalContent.js';

export default function Retreat() {
  return (
    <section id="retreat" className="retreat-section content-section" aria-labelledby="retreat-title">
      <div className="page-shell">
        <div className="retreat-intro"><div><span className="eyebrow">{retreat.eyebrow}</span><h2 id="retreat-title">{retreat.title}</h2></div><p>{retreat.description}</p></div>
        <div className="retreat-features">{retreat.features.map((feature) => <article key={feature.title}><h3>{feature.title}</h3><p>{feature.description}</p></article>)}</div>
      </div>
    </section>
  );
}
