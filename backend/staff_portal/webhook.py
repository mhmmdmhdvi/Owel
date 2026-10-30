import json

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import PortalSession, TelegramConnection, TelegramDelivery, TelegramUpdate


@csrf_exempt
@require_POST
def telegram_webhook(request):
    if not settings.TELEGRAM_WEBHOOK_SECRET or not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_MINI_APP_URL:
        return JsonResponse({'detail': 'Not configured'}, status=503)
    secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
    if not constant_time_compare(secret, settings.TELEGRAM_WEBHOOK_SECRET):
        return JsonResponse({'detail': 'Forbidden'}, status=403)
    try:
        data = json.loads(request.body)
        message = data.get('message', {})
        sender = message.get('from', {})
        chat = message.get('chat', {})
        identity = sender.get('id')
        update_id = data.get('update_id')
        text = message.get('text') or ''
        if not isinstance(text, str):
            return JsonResponse({'ok': True})
        command = (text.split(maxsplit=1) or [''])[0].split('@', 1)[0]
        if chat.get('type') != 'private' or type(identity) is not int or not 0 < identity < 2**63 or chat.get('id') != identity or sender.get('is_bot'):
            return JsonResponse({'ok': True})
        if command not in ['/start', '/stop'] or type(update_id) is not int or not 0 <= update_id < 2**63:
            return JsonResponse({'ok': True})
    except (ValueError, TypeError, AttributeError, IndexError):
        return JsonResponse({'detail': 'Invalid update'}, status=400)
    with transaction.atomic():
        _, created = TelegramUpdate.objects.get_or_create(update_id=update_id)
        if created:
            if command == '/stop':
                TelegramConnection.objects.filter(telegram_user_id=identity).update(active=False)
                PortalSession.objects.filter(telegram_user_id=identity).delete()
            # Collapse repeated menu requests in the same minute.
            key = f'{command}:{identity}:{int(timezone.now().timestamp()) // 60}'
            TelegramDelivery.objects.get_or_create(dedupe_key=key, defaults={
                'kind': 'menu' if command == '/start' else 'stopped',
                'chat_id': identity, 'next_attempt_at': timezone.now(),
            })
    return JsonResponse({'ok': True})
