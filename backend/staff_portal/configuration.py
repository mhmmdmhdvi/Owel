import ipaddress
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import CommandError


def require_public_url(value, name):
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ''
        if parsed.scheme != 'https' or not host or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError
        if host.lower() == 'localhost' or host.lower().endswith(('.localhost', '.local')):
            raise ValueError
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address and not address.is_global:
            raise ValueError
    except ValueError:
        raise CommandError(f'{name} must be a public HTTPS URL without credentials, query, or fragment.') from None


def require_telegram_configuration():
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_SECRET:
        raise CommandError('Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET in backend/.env first.')
    if not 32 <= len(settings.TELEGRAM_WEBHOOK_SECRET) <= 256:
        raise CommandError('TELEGRAM_WEBHOOK_SECRET must have 32 to 256 random characters.')
    require_public_url(settings.TELEGRAM_MINI_APP_URL, 'TELEGRAM_MINI_APP_URL')
