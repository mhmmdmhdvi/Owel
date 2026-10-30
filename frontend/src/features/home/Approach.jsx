import { approaches, approachIntro } from './content.js';

export default function Approach() {
  return (
    <section id="approach" className="approach-section" aria-labelledby="approach-title">
      <div className="page-shell">
        <div className="approach-heading flex flex-wrap items-end justify-between gap-6">
          <div><span className="eyebrow">{approachIntro.eyebrow}</span><h2 id="approach-title">{approachIntro.title}</h2></div>
        </div>
        <p className="approach-description">{approachIntro.description}</p>
        <div className="approach-grid grid md:grid-cols-3">
          {approaches.map((approach) => (
            <article className="approach-item" key={approach.number}>
              <span className="approach-number">{approach.number}</span>
              <h3>{approach.title}</h3>
              <p>{approach.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
