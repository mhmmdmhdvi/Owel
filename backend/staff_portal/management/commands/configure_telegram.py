from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from staff_portal.client import TelegramError, call_telegram
from staff_portal.configuration import require_public_url, require_telegram_configuration


class Command(BaseCommand):
    help = 'Activate the configured Telegram webhook, commands, and Mini App menu.'

    def handle(self, *args, **options):
        require_telegram_configuration()
        require_public_url(settings.TELEGRAM_WEBHOOK_URL, 'TELEGRAM_WEBHOOK_URL')
        try:
            bot = call_telegram('getMe', {})
            call_telegram('setWebhook', {
                'url': settings.TELEGRAM_WEBHOOK_URL, 'secret_token': settings.TELEGRAM_WEBHOOK_SECRET,
                'allowed_updates': ['message'], 'drop_pending_updates': False,
            })
            call_telegram('setMyCommands', {'commands': [
                {'command': 'start', 'description': 'ورود به پنل مدیریت'},
                {'command': 'stop', 'description': 'غیرفعال‌کردن اعلان‌ها و دسترسی تلگرام'},
            ]})
            call_telegram('setChatMenuButton', {'menu_button': {
                'type': 'web_app', 'text': 'پنل مدیریت', 'web_app': {'url': settings.TELEGRAM_MINI_APP_URL},
            }})
        except TelegramError as error:
            raise CommandError(f'Telegram configuration failed ({error.code}).') from None
        self.stdout.write(self.style.SUCCESS(f'Telegram bot @{bot["username"]} configured. Start telegram_worker to deliver messages.'))
