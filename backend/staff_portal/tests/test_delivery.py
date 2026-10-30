from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.utils import timezone

from reservations.models import ReservationRequest
from staff_portal.client import TelegramError
from staff_portal.delivery import claim_delivery, deliver_one, queue_reservation
from staff_portal.models import TelegramConnection, TelegramDelivery


@override_settings(TELEGRAM_MINI_APP_URL='https://owel.example/staff')
class DeliveryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('recipient', is_staff=True)
        self.user.user_permissions.add(Permission.objects.get(codename='view_reservationrequest'))
        self.connection = TelegramConnection.objects.create(user=self.user, telegram_user_id=12345)
        self.reservation = ReservationRequest.objects.create(full_name='Private Name', email='private@example.com', whatsapp='+12025550123')
        queue_reservation(self.reservation)

    def test_sent_notification_contains_only_request_number_and_panel_link(self):
        sent = []
        with patch('staff_portal.delivery.send_message', side_effect=lambda payload: sent.append(payload)):
            self.assertTrue(deliver_one())
        job = TelegramDelivery.objects.get()
        self.assertIsNotNone(job.sent_at)
        self.assertIn(str(self.reservation.pk), sent[0]['text'])
        for contact in ['Private Name', 'private@example.com', '+12025550123']:
            self.assertNotIn(contact, str(sent[0]))
        self.assertFalse(deliver_one())

    def test_retry_after_is_honored_and_lease_released(self):
        with patch('staff_portal.delivery.send_message', side_effect=TelegramError('http_429', retry_after=120)):
            self.assertTrue(deliver_one())
        job = TelegramDelivery.objects.get()
        self.assertIsNone(job.sent_at)
        self.assertIsNone(job.lease_until)
        self.assertGreater(job.next_attempt_at, timezone.now() + timedelta(seconds=115))
        self.assertFalse(deliver_one())

    def test_revoked_recipient_and_removed_permission_cancel_delivery(self):
        self.connection.active = False
        self.connection.save()
        with patch('staff_portal.delivery.send_message', side_effect=AssertionError('must not send')):
            self.assertTrue(deliver_one())
        self.assertEqual(TelegramDelivery.objects.get().last_error, 'access_revoked')

    def test_claimed_job_cannot_be_claimed_twice_during_lease(self):
        self.assertIsNotNone(claim_delivery())
        self.assertIsNone(claim_delivery())

    def test_repeated_queue_is_deduplicated(self):
        queue_reservation(self.reservation)
        self.assertEqual(TelegramDelivery.objects.count(), 1)
