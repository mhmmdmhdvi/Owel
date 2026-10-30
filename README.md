# Owel

Website for one psychologist. The two folders are independent, with no root npm package or shared dependency directory.

## Local development

Run the frontend from its own folder:

```sh
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (normally http://127.0.0.1:5173). See [frontend/README.md](frontend/README.md) for frontend commands and [backend/README.md](backend/README.md) for backend status.

```sh
npm run build
npm run preview
npm test
```

Build and test commands above also run from `frontend/`.

## Structure

```text
frontend/
  src/
    components/layout/  Header and footer
    components/ui/      Shared brand and functional icons
    features/home/      Homepage sections and content
    styles.css          Theme, font, and responsive styles
  public/images/        Local responsive WebP photographs
  tests/                Browser interaction checks
```

`frontend/src/features/home/content.js` keeps text from the supplied HTML separate from rendering. Reservation links open the contact-request page; service rows expand to show details. Payments are not connected.

`backend/` contains the Django REST Framework reservation API, staff authentication, Django admin, and Telegram notification worker, backed by PostgreSQL. Start it alongside the frontend using [backend/README.md](backend/README.md). Reservations collect only a name, email address, and WhatsApp number. The `/staff` panel works locally; live Telegram activation requires a bot token and public HTTPS URLs.

See [frontend/ASSETS.md](frontend/ASSETS.md) for photograph and font credits.
