import hashlib
import hmac
import json
import time
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import urlencode

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase


def signed_init_data(user_id=12345, **changes):
    data = {'auth_date': str(int(time.time())), 'user': json.dumps({'id': user_id, 'first_name': 'Test'}, separators=(',', ':'))}
    data.update(changes)
    check = '\n'.join(f'{key}={value}' for key, value in sorted(data.items()))
    secret = hmac.new(b'WebAppData', b'123:test-token', hashlib.sha256).digest()
    data['hash'] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(data)


@override_settings(TELEGRAM_BOT_TOKEN='123:test-token', TELEGRAM_WEBHOOK_SECRET='test-hook-secret', TELEGRAM_MINI_APP_URL='https://owel.example/staff')
class StaffAccessTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user('employer', password='test-staff-password', is_staff=True)
        self.user.user_permissions.add(*Permission.objects.filter(codename__in=['view_reservationrequest', 'change_reservationrequest']))

    def login(self, **changes):
        return self.client.post('/api/staff/login/', {'username': 'employer', 'password': 'test-staff-password', **changes}, format='json')

    def authorize(self, **changes):
        response = self.login(**changes)
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.json()['token'])
        return response

    def test_login_and_list_require_staff_permissions(self):
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 401)
        response = self.authorize()
        self.assertNotIn('password', response.json())
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 200)
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 403)

    def test_three_failures_lock_for_fifteen_minutes_and_expire(self):
        self.assertEqual([self.login(password='wrong').status_code for _ in range(3)], [401, 401, 429])
        cache.clear()
        self.assertEqual(self.login().status_code, 429)
        with patch('staff_portal.backends.timezone.now', return_value=timezone.now() + timedelta(minutes=16)):
            self.assertEqual(self.login().status_code, 200)

    def test_success_resets_failed_attempts(self):
        self.assertEqual(self.login(password='wrong').status_code, 401)
        self.assertEqual(self.login().status_code, 200)
        self.assertEqual(self.login(password='wrong').status_code, 401)
        self.assertEqual(self.login(password='wrong').status_code, 401)

    def test_admin_and_portal_share_the_same_attempt_counter(self):
        for _ in range(2):
            self.client.post('/admin/login/', {'username': 'employer', 'password': 'wrong'})
        self.assertEqual(self.login(password='wrong').status_code, 429)
        response = self.client.post('/admin/login/', {'username': 'employer', 'password': 'test-staff-password'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_password_change_and_logout_invalidate_tokens(self):
        self.authorize()
        self.assertEqual(self.client.post('/api/staff/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 401)
        self.authorize()
        self.user.set_password('changed-test-password')
        self.user.save()
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 401)

    def test_logout_still_revokes_token_after_view_permission_is_removed(self):
        self.authorize()
        self.user.user_permissions.remove(Permission.objects.get(codename='view_reservationrequest'))
        self.assertEqual(self.client.post('/api/staff/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 401)

    def test_valid_telegram_data_binds_account_and_revocation_blocks_session(self):
        response = self.authorize(telegram_init_data=signed_init_data())
        self.assertTrue(response.json()['user']['telegram_connected'])
        connection = apps.get_model('staff_portal', 'TelegramConnection').objects.get()
        self.assertEqual(connection.telegram_user_id, 12345)
        connection.active = False
        connection.save()
        self.assertEqual(self.client.get('/api/staff/reservations/').status_code, 401)

    def test_tampered_expired_future_duplicate_and_bot_telegram_data_are_rejected(self):
        malformed = [
            signed_init_data().replace('12345', '54321'),
            signed_init_data(auth_date=str(int(time.time()) - 600)),
            signed_init_data(auth_date=str(int(time.time()) + 600)),
            signed_init_data() + '&auth_date=1',
            signed_init_data(user=json.dumps({'id': 12345, 'is_bot': True})),
        ]
        for data in malformed:
            with self.subTest(data=data[:25]):
                self.assertEqual(self.login(telegram_init_data=data).status_code, 400)
        self.assertFalse(apps.get_model('staff_portal', 'TelegramConnection').objects.exists())

    def test_existing_binding_cannot_silently_move_to_another_telegram_account(self):
        self.authorize(telegram_init_data=signed_init_data())
        self.assertEqual(self.login(telegram_init_data=signed_init_data(67890)).status_code, 409)
        connection = apps.get_model('staff_portal', 'TelegramConnection').objects.get()
        self.assertEqual(connection.telegram_user_id, 12345)

    def test_list_search_filter_and_review_enforce_change_permission(self):
        from reservations.models import ReservationRequest
        first = ReservationRequest.objects.create(full_name='Test One', email='one@example.com', whatsapp='+12025550123')
        ReservationRequest.objects.create(full_name='Test Two', email='two@example.com', whatsapp='+12025550124', handled=True)
        self.authorize()
        response = self.client.get('/api/staff/reservations/?q=one&status=new')
        self.assertEqual(response.json()['count'], 1)
        detail = f'/api/staff/reservations/{first.pk}/'
        self.assertEqual(self.client.patch(detail, {'handled': True, 'full_name': 'injected'}, format='json').status_code, 200)
        first.refresh_from_db()
        self.assertTrue(first.handled)
        self.assertEqual(first.full_name, 'Test One')
        self.user.user_permissions.remove(Permission.objects.get(codename='change_reservationrequest'))
        self.assertEqual(self.client.patch(detail, {'handled': False}, format='json').status_code, 403)

    def test_webhook_requires_secret_private_chat_and_deduplicates_updates(self):
        payload = {'update_id': 91, 'message': {'text': '/start', 'from': {'id': 12345}, 'chat': {'id': 12345, 'type': 'private'}}}
        url = '/api/telegram/webhook/'
        self.assertEqual(self.client.post(url, payload, format='json').status_code, 403)
        for _ in range(2):
            self.assertEqual(self.client.post(url, payload, format='json', HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN='test-hook-secret').status_code, 200)
        delivery = apps.get_model('staff_portal', 'TelegramDelivery')
        self.assertEqual(delivery.objects.count(), 1)
        payload['update_id'] = 92
        payload['message']['chat']['type'] = 'group'
        self.client.post(url, payload, format='json', HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN='test-hook-secret')
        self.assertEqual(delivery.objects.count(), 1)

    def test_submission_queues_notification_without_sending_personal_data(self):
        self.authorize(telegram_init_data=signed_init_data())
        self.client.credentials()
        response = self.client.post('/api/reservations/', {'full_name': 'Private Client', 'email': 'private@example.com', 'whatsapp': '+12025550123'}, format='json')
        self.assertEqual(response.status_code, 201)
        delivery = apps.get_model('staff_portal', 'TelegramDelivery').objects.get(kind='reservation')
        self.assertEqual(delivery.chat_id, 12345)
        self.assertIsNotNone(delivery.reservation_id)
        self.assertIsNone(delivery.sent_at)

    def test_non_text_webhook_messages_are_acknowledged_without_queueing(self):
        response = self.client.post('/api/telegram/webhook/', {
            'update_id': 99, 'message': {'from': {'id': 12345}, 'chat': {'id': 12345, 'type': 'private'}, 'photo': []},
        }, format='json', HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN='test-hook-secret')
        self.assertEqual(response.status_code, 200)
