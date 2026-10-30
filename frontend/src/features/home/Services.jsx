import Icon from '../../components/ui/Icon.jsx';
import { services, servicesIntro } from './content.js';
import { useState } from 'react';

function ServiceRow({ service }) {
  const [expanded, setExpanded] = useState(false);
  const panelId = `${service.id}-details`;
  const titleId = `${service.id}-title`;

  return (
    <article className="service-row" id={service.id}>
      <h3>
        <button className="service-trigger" type="button" aria-expanded={expanded} aria-controls={panelId} onClick={() => setExpanded(!expanded)}>
          <span className="service-number">{service.number}</span>
          <span className="service-titles"><span className="service-title" id={titleId}>{service.title}</span><span className="service-subtitle">{service.subtitle}</span></span>
          <span className={`service-toggle ${expanded ? 'is-expanded' : ''}`}><Icon name="plus" /></span>
        </button>
      </h3>
      <div className="service-details" id={panelId} role="region" aria-labelledby={titleId} hidden={!expanded}>
        {service.description && <p className="service-description">{service.description}</p>}
        <ul className="flex flex-wrap gap-x-8 gap-y-3">{service.details.map((detail) => <li key={detail}>{detail}</li>)}</ul>
      </div>
    </article>
  );
}

export default function Services() {
  return (
    <section id="services" className="services-section" aria-labelledby="services-title">
      <div className="page-shell section-split">
        <div className="section-intro">
          <h2 id="services-title">{servicesIntro.title}</h2>
          <p>{servicesIntro.description}</p>
        </div>
        <div className="service-list">{services.map((service) => <ServiceRow key={service.id} service={service} />)}</div>
      </div>
    </section>
  );
}
