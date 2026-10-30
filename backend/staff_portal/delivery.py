import uuid
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .client import TelegramError, send_message
from .models import TelegramConnection, TelegramDelivery


def can_receive(connection):
    return bool(connection and connection.active and connection.user.is_active and connection.user.is_staff and connection.user.has_perm('reservations.view_reservationrequest'))


def queue_reservation(reservation):
    now = timezone.now()
    connections = TelegramConnection.objects.select_for_update(of=('self',)).select_related('user').filter(active=True)
    deliveries = [TelegramDelivery(
        dedupe_key=f'reservation:{reservation.pk}:{connection.pk}',
        kind='reservation', reservation=reservation, connection=connection,
        chat_id=connection.telegram_user_id, next_attempt_at=now,
    ) for connection in connections if can_receive(connection)]
    TelegramDelivery.objects.bulk_create(deliveries, ignore_conflicts=True)


def login_button():
    return {'inline_keyboard': [[{'text': 'ورود به پنل', 'web_app': {'url': settings.TELEGRAM_MINI_APP_URL}}]]}


@transaction.atomic
def claim_delivery():
    now = timezone.now()
    job = TelegramDelivery.objects.select_for_update(skip_locked=True).filter(
        sent_at__isnull=True, cancelled_at__isnull=True, next_attempt_at__lte=now,
    ).filter(Q(lease_until__isnull=True) | Q(lease_until__lte=now)).first()
    if job:
        job.lease_id = uuid.uuid4()
        job.lease_until = now + timedelta(seconds=60)
        job.attempts += 1
        job.save(update_fields=['lease_id', 'lease_until', 'attempts'])
    return job


def deliver_one():
    job = claim_delivery()
    if not job:
        return False
    owned = TelegramDelivery.objects.filter(pk=job.pk, lease_id=job.lease_id)
    if job.kind == 'reservation':
        connection = TelegramConnection.objects.select_related('user').filter(pk=job.connection_id).first()
        if not can_receive(connection) or connection.telegram_user_id != job.chat_id:
            owned.update(cancelled_at=timezone.now(), lease_until=None, last_error='access_revoked')
            return True
        text = f'درخواست رزرو جدید #{job.reservation_id}'
    elif job.kind == 'menu':
        text = 'برای ورود به پنل، دکمه زیر را بزنید.'
    else:
        text = 'اعلان‌های این حساب غیرفعال شد.'
    payload = {'chat_id': job.chat_id, 'text': text}
    if job.kind != 'stopped':
        payload['reply_markup'] = login_button()
    try:
        send_message(payload)
    except TelegramError as error:
        delay = max(error.retry_after, min(3600, 5 * (2 ** min(job.attempts, 10))))
        updates = {'lease_until': None, 'last_error': error.code, 'next_attempt_at': timezone.now() + timedelta(seconds=delay)}
        if error.permanent:
            updates['cancelled_at'] = timezone.now()
        owned.update(**updates)
    else:
        owned.update(sent_at=timezone.now(), lease_until=None, last_error='')
    return True
