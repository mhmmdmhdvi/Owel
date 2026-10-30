import time

from django.core.management.base import BaseCommand, CommandError

from staff_portal.configuration import require_telegram_configuration
from staff_portal.delivery import deliver_one


class Command(BaseCommand):
    help = 'Deliver queued Telegram notifications. Run as a separate process in production.'

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='Process up to 100 due messages and exit.')
        parser.add_argument('--interval', type=int, default=3)

    def handle(self, *args, **options):
        require_telegram_configuration()
        if not 1 <= options['interval'] <= 60:
            raise CommandError('Interval must be between 1 and 60 seconds.')
        try:
            while True:
                count = 0
                while count < 100 and deliver_one():
                    count += 1
                if options['once']:
                    self.stdout.write(f'Processed {count} queued messages.')
                    return
                time.sleep(options['interval'])
        except KeyboardInterrupt:
            self.stdout.write('Worker stopped.')
