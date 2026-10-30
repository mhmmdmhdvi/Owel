from http.client import IncompleteRead
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from django.test import SimpleTestCase, override_settings

from staff_portal.client import TelegramError, call_telegram


@override_settings(TELEGRAM_BOT_TOKEN='123:dummy-test-token')
class TelegramTransportTests(SimpleTestCase):
    def test_truncated_success_response_becomes_retryable_error(self):
        response = Mock()
        response.read.side_effect = IncompleteRead(b'{"ok":', 30)
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        with patch('staff_portal.client.urlopen', return_value=context):
            with self.assertRaises(TelegramError) as captured:
                call_telegram('sendMessage', {'chat_id': 1, 'text': 'test'})
        self.assertEqual(captured.exception.code, 'network_error')
        self.assertFalse(captured.exception.permanent)

    def test_error_body_timeout_becomes_retryable_error(self):
        body = Mock()
        body.read.side_effect = TimeoutError('interrupted')
        failure = HTTPError('https://api.telegram.org/redacted', 503, 'unavailable', {}, body)
        with patch('staff_portal.client.urlopen', side_effect=failure):
            with self.assertRaises(TelegramError) as captured:
                call_telegram('sendMessage', {'chat_id': 1, 'text': 'test'})
        self.assertEqual(captured.exception.code, 'http_503')
        self.assertFalse(captured.exception.permanent)
