# Owel backend

Django REST Framework and PostgreSQL store reservation contact requests. Django admin and the React staff panel provide a staff-only list, search, review flag, and internal notes. Visitors do not need accounts and receive only a submission confirmation.

## Setup

From this folder, create a virtual environment and install dependencies:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -r requirements.txt
# Linux:
.venv/bin/python -m pip install -r requirements.txt
```

For a new checkout, copy `.env.example` to `.env` and configure a secret key and an existing PostgreSQL database/user. The local development environment already has an ignored `.env` configured for its project database on port 5440. Environment variables override `.env` values.

```sh
# Windows (use .venv/bin/python on Linux):
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/admin/. For this prepared local environment, generated administrator credentials are in ignored `.local/admin-access.txt`. That local account and file are not part of the repository.

The prepared Windows development cluster is in ignored `.local/postgres`. Start it after a restart with:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe' -D "$PWD\.local\postgres" -l "$PWD\.local\postgres.log" -o '-p 5440 -h 127.0.0.1' -w start
```

For Ubuntu production, use its PostgreSQL service, a dedicated database role, the real host/domain in `DJANGO_ALLOWED_HOSTS`, a new secret, HTTPS, and `DJANGO_DEBUG=False`. Route `/api/`, `/admin/`, and Django static files to this backend; serve the frontend separately. Never deploy `.local/` or the local development database/account.

## API

`POST /api/reservations/` accepts JSON:

```json
{"full_name":"Example Visitor","email":"visitor@example.com","whatsapp":"+12025550123"}
```

Success is HTTP 201 with `{"message":"درخواست شما ثبت شد."}`. Invalid fields return HTTP 400 with field errors. No public list, detail, edit, or deletion API is exposed. Only the three contact fields are writable by visitors. Five requests per minute per client IP are allowed by the application throttle; production reverse-proxy rate limiting can supplement it.

Names and email are validated and WhatsApp numbers are normalized to international form, including Persian/Arabic numerals. No date, time, availability, payment, or medical details are collected. `handled` and internal notes are staff-only fields.

## Employer access

Open http://127.0.0.1:5173/staff. The prepared local employer credentials are in ignored `.local/staff-access.txt`. The same account can log into Django admin. It belongs to the `Reservation managers` group, which has only reservation view/change permissions, without user management or deletion permissions.

For another account, run the command below. It prompts for a password without storing it in terminal history:

```sh
.venv\Scripts\python manage.py create_reservation_staff employer-name
```

Both entry points share a PostgreSQL-backed failure counter: three failed password attempts lock that username for 15 minutes. Success resets the counter; restarting services does not remove a lock. A superuser can unlock an account under Login guards in Django admin. Portal access tokens are stored only as hashes on the server, held only in browser memory, and expire after eight hours. Reloading the panel requires login again. Password changes, account disabling, permission removal, logout, and Telegram access revocation invalidate access.

## Telegram activation

The bot implementation is included, but real messages are disabled until credentials and public HTTPS URLs are configured. Get a bot token from BotFather and put these settings in ignored `backend/.env`:

```dotenv
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_SECRET=at-least-32-random-characters
TELEGRAM_MINI_APP_URL=https://your-domain.example/staff
TELEGRAM_WEBHOOK_URL=https://your-domain.example/api/telegram/webhook/
```

Generate the webhook secret with `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Do not put tokens or real passwords in source files, frontend environment variables, or Telegram chat. Restart Django after changing `.env`.

After deployment, activate the webhook/menu and run the separate notification worker:

```sh
.venv\Scripts\python manage.py configure_telegram
.venv\Scripts\python manage.py telegram_worker
# Alternatively process up to 100 due messages for a one-shot/cron run:
.venv\Scripts\python manage.py telegram_worker --once
```

Use `.venv/bin/python` on Ubuntu. Run Django and the worker as separate supervised processes. The frontend and API must share the same public origin; proxy `/api/` to Django and serve `/staff` through the frontend SPA fallback. Telegram Web clients embed Mini Apps: frontend response frame restrictions must allow Telegram Web, rather than applying Django admin's `DENY` header to the static staff page.

The employer opens the private bot chat, sends `/start`, and taps **ورود به پنل**. They enter their Django username/password on the web form, outside chat. The backend verifies the Telegram HMAC and its timestamp before binding the numeric user ID. A binding cannot silently transfer to another Telegram account; a superuser must delete the old connection before a transfer. `/stop` disables that account's Telegram connection and revokes its Telegram-bound portal tokens. A later valid login from the same Telegram ID can reactivate it. Admins can also revoke a connection through Django admin.

The webhook requires its secret header and accepts only private sender/chat matches. Updates are deduplicated. Notification rows are queued in the same database transaction as reservations and sent by the worker after current recipient permissions are checked. Messages contain only the reservation number and a panel button; contact details stay behind login. Transient network failures and Telegram rate limits retry with backoff. Telegram delivery is at-least-once: an ambiguous network failure after Telegram accepted a message may produce a duplicate on retry. The original reservation remains in PostgreSQL regardless of Telegram availability.

Staff APIs use explicit, short-lived Bearer tokens and never accept Django admin cookies as staff-panel authorization. No CORS or third-party-cookie dependency is needed. The standard Django admin keeps its normal cookie/CSRF protections. The Telegram-only webhook is CSRF-exempt and instead validates the configured secret header.

## Checks

```sh
.venv\Scripts\python manage.py check
.venv\Scripts\python manage.py makemigrations --check --dry-run
.venv\Scripts\python manage.py test
```

Tests use a temporary PostgreSQL database. The development test database role needs permission to create databases. Dependencies, configuration, migrations, and tests stay inside `backend/`; secrets, runtime data, and AI scratch work are ignored.
