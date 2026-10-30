import Icon from '../../components/ui/Icon.jsx';

export default function MediaCard({ item }) {
  const audio = item.format === 'audio';

  return (
    <article className={`media-card media-card-${item.format}`}>
      <div className={`media-artwork ${audio ? 'podcast-artwork' : 'video-artwork'}`} aria-hidden="true">
        {audio ? (
          <div className="podcast-cover">
            <span className="podcast-cover-brand" lang="en" dir="ltr">owel.</span>
            <span className="podcast-cover-title">{item.coverTitle}</span>
            <span className="podcast-cover-episode">{item.episode}</span>
          </div>
        ) : (
          <img
            src={item.thumbnail}
            srcSet="/images/landscape-640.webp 640w, /images/landscape-1100.webp 1100w"
            sizes="(max-width: 767px) calc(100vw - 40px), (max-width: 1200px) 45vw, 580px"
            width="1100" height="733" alt="" loading="lazy" decoding="async"
          />
        )}
        <span className="media-format-icon"><Icon name={audio ? 'headphones' : 'play'} /></span>
        {audio && <span className="media-duration">{item.note}</span>}
      </div>
      <div className="media-card-body">
        <div className="media-card-channel">
          <span className={`media-channel-icon ${audio ? 'audio-channel-icon' : ''}`} aria-hidden="true"><Icon name={audio ? 'headphones' : 'play'} /></span>
          <span>{item.type}</span>
          {!audio && <span className="media-card-note">{item.note}</span>}
        </div>
        <h3>{item.title}</h3>
        <p>{item.description}</p>
      </div>
    </article>
  );
}
