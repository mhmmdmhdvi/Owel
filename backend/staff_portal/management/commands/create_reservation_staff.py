import getpass
import secrets
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a staff account limited to viewing and reviewing reservations.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('--generate-local', action='store_true', help='DEBUG only: generate credentials in ignored .local/staff-access.txt.')

    def handle(self, *args, **options):
        username = get_user_model().normalize_username(options['username']).strip()
        if get_user_model().objects.filter(username=username).exists():
            raise CommandError('That username already exists. No account was changed.')
        if options['generate_local']:
            if not settings.DEBUG:
                raise CommandError('--generate-local is only available with DJANGO_DEBUG=True.')
            password = secrets.token_urlsafe(24)
        else:
            password = getpass.getpass('Password: ')
            if password != getpass.getpass('Password again: '):
                raise CommandError('Passwords do not match.')
        user = get_user_model()(username=username, is_staff=True)
        try:
            user.full_clean(exclude=['password'])
            validate_password(password, user=user)
        except ValidationError as error:
            raise CommandError('; '.join(error.messages)) from None
        with transaction.atomic():
            user.set_password(password)
            user.save()
            group, _ = Group.objects.get_or_create(name='Reservation managers')
            group.permissions.set(Permission.objects.filter(content_type__app_label='reservations', codename__in=['view_reservationrequest', 'change_reservationrequest']))
            user.groups.add(group)
        if options['generate_local']:
            destination = Path(settings.BASE_DIR) / '.local' / 'staff-access.txt'
            destination.parent.mkdir(exist_ok=True)
            destination.write_text(f'LOCAL STAFF ACCESS\nPanel: http://127.0.0.1:5173/staff\nAdmin: http://127.0.0.1:8000/admin/\nUsername: {username}\nPassword: {password}\n', encoding='utf-8')
            self.stdout.write('Local credentials saved in ignored backend/.local/staff-access.txt.')
        self.stdout.write(self.style.SUCCESS('Reservation staff account created.'))
