# Owel frontend

Persian RTL homepage built with React, Vite, and Tailwind CSS. Noto Sans Arabic and responsive WebP photographs are served locally. Homepage copy comes from the supplied `owel.html`; the original layout is not reused beyond the requested full-section hero background.

## Development

Run these commands from this `frontend` directory:

```sh
npm install
npm run dev
```

Vite serves http://127.0.0.1:5173 by default.

```sh
npm run build
npm run preview
npm test
```

Browser checks use locally installed Google Chrome. If Chrome is unavailable, adjust `playwright.config.js` to use a Playwright-managed Chromium installation.

## Structure

- `src/components/layout`: header and footer.
- `src/components/ui`: shared text brand and interface icons.
- `src/features/home`: homepage sections and source copy in `content.js`.
- `src/features/home/coursesContent.js` and `additionalContent.js`: additional course, retreat, introduction, and media text from the original HTML.
- `src/styles.css`: typography, theme, and responsive styles.
- `public`: photographs, favicon, and font license.
- `tests`: browser interaction and hero layout checks.

Dependencies, build output, tests, and configuration are contained here. `/reservation` collects only name, email, and WhatsApp number. It submits to the Django API through Vite's same-origin `/api` proxy and shows a simple confirmation after persistence. Backend errors retain entered values. Payments are not connected.

`/staff` is a separate, lazily loaded staff interface for username/password login, reservation search/filter/pagination, contact details, review notes, and logout. It works in a normal browser and as a Telegram Mini App. Its access token stays only in React memory, with no localStorage/sessionStorage persistence. Telegram launch data is passed to the backend for signature verification; client-provided identities are never trusted. See `../backend/README.md` for the prepared local employer account and live Telegram activation.

For browser tests, first prepare the backend virtualenv, `.env`, PostgreSQL database, and migrations as described in `../backend/README.md`. Playwright starts or reuses both development servers. End-to-end reservation checks verify the real database row and remove their own test records.

For a static production build, route `/reservation` through the frontend's `index.html` fallback and proxy `/api/` to Django on the same site. No database credentials or backend secrets belong in frontend environment variables or build assets.

All courses are shown in compact cards. Full course descriptions and topics expand under each card's disclosure. The circular floating up-arrow appears after scrolling, returns to the top, and honors reduced-motion preferences. Media cards use a 16:9 preview layout: a typographic podcast cover and a temporary landscape video thumbnail. Media URLs and playback are not configured yet. No play badges are interactive until actual media destinations are supplied.

See [ASSETS.md](ASSETS.md) for image and font credits.
