import json
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class TelegramError(Exception):
    def __init__(self, code, *, permanent=False, retry_after=0):
        super().__init__(code)
        self.code = code
        self.permanent = permanent
        self.retry_after = retry_after


def call_telegram(method, payload):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise TelegramError('not_configured')
    request = Request(
        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}',
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={'Content-Type': 'application/json'}, method='POST',
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except HTTPError as error:
        try:
            with error:
                data = json.loads(error.read())
            retry = int(data.get('parameters', {}).get('retry_after', 0))
        except (ValueError, TypeError, AttributeError, OSError, HTTPException):
            retry = 0
        raise TelegramError(f'http_{error.code}', permanent=400 <= error.code < 500 and error.code != 429, retry_after=retry) from None
    except (URLError, TimeoutError, OSError, ValueError, HTTPException):
        raise TelegramError('network_error') from None
    if not isinstance(data, dict) or not data.get('ok'):
        raise TelegramError('invalid_response')
    return data.get('result')


def send_message(payload):
    return call_telegram('sendMessage', payload)
