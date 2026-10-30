import { about } from './additionalContent.js';

export default function About() {
  return (
    <section id="about" className="about-section content-section" aria-labelledby="about-title">
      <div className="page-shell about-grid">
        <div className="content-heading"><span className="eyebrow">{about.eyebrow}</span><h2 id="about-title">{about.title}</h2><p>{about.description}</p></div>
        <figure className="about-quote"><blockquote>{about.quote}</blockquote><figcaption>{about.role}</figcaption></figure>
      </div>
    </section>
  );
}
