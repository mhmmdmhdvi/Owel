import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException, ValidationError

from .models import TelegramConnection


class BindingConflict(APIException):
    status_code = 409
    default_detail = 'این حساب قبلاً به تلگرام متصل شده است. برای تغییر اتصال با مدیر تماس بگیرید.'


def verify_init_data(raw):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValidationError('اتصال تلگرام هنوز پیکربندی نشده است.')
    try:
        if not isinstance(raw, str) or len(raw) > 10000:
            raise ValueError
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True, max_num_fields=30, errors='strict')
        data = dict(pairs)
        if len(data) != len(pairs):
            raise ValueError
        signature = data.pop('hash')
        if len(signature) != 64:
            raise ValueError
        check = '\n'.join(f'{key}={value}' for key, value in sorted(data.items()))
        secret = hmac.new(b'WebAppData', settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        age = time.time() - int(data['auth_date'])
        if not -30 <= age <= 300:
            raise ValueError
        user = json.loads(data['user'])
        identity = user['id']
        if type(identity) is not int or not 0 < identity < 2**63 or user.get('is_bot'):
            raise ValueError
        if data.get('chat_type', 'private') not in ['private', 'sender']:
            raise ValueError
        if 'chat' in data and json.loads(data['chat']).get('type') != 'private':
            raise ValueError
        return identity
    except (ValueError, KeyError, TypeError, AttributeError, UnicodeError):
        raise ValidationError('اطلاعات ورود تلگرام معتبر نیست. پنل را دوباره از ربات باز کنید.') from None


def bind_telegram(user, identity):
    try:
        with transaction.atomic():
            get_user_model().objects.select_for_update().get(pk=user.pk)
            connection = TelegramConnection.objects.filter(user=user).first()
            if connection and connection.telegram_user_id != identity:
                raise BindingConflict()
            if connection:
                connection.active = True
                connection.save(update_fields=['active'])
            else:
                TelegramConnection.objects.create(user=user, telegram_user_id=identity)
    except IntegrityError:
        raise BindingConflict() from None
