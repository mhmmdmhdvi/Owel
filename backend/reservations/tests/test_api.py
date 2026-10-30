from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase


class ReservationAPITests(APITestCase):
    endpoint = '/api/reservations/'

    def setUp(self):
        cache.clear()
        self.payload = {
            'full_name': 'Test Visitor',
            'email': 'visitor@example.com',
            'whatsapp': '+1 (202) 555-0123',
        }

    def post(self, **changes):
        return self.client.post(self.endpoint, {**self.payload, **changes}, format='json')

    def test_contact_request_is_saved_with_simple_confirmation(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message': 'درخواست شما ثبت شد.'})
        reservation = apps.get_model('reservations', 'ReservationRequest').objects.get()
        self.assertEqual(reservation.full_name, 'Test Visitor')
        self.assertEqual(reservation.email, 'visitor@example.com')
        self.assertEqual(reservation.whatsapp, '+12025550123')
        self.assertFalse(reservation.handled)

    def test_invalid_contact_details_are_rejected(self):
        for field, value in [('full_name', ' '), ('email', 'invalid'), ('whatsapp', 'hello'), ('whatsapp', '12345')]:
            with self.subTest(field=field, value=value):
                cache.clear()
                response = self.post(**{field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json())

    def test_persian_phone_digits_are_normalized(self):
        response = self.post(whatsapp='+۱ ۲۰۲ ۵۵۵ ۰۱۲۳')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(apps.get_model('reservations', 'ReservationRequest').objects.get().whatsapp, '+12025550123')

    def test_missing_fields_are_rejected_without_creating_a_request(self):
        response = self.client.post(self.endpoint, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {'full_name', 'email', 'whatsapp'})
        self.assertEqual(apps.get_model('reservations', 'ReservationRequest').objects.count(), 0)

    def test_public_cannot_set_administrative_fields(self):
        response = self.post(handled=True, admin_notes='injected')
        self.assertEqual(response.status_code, 201)
        reservation = apps.get_model('reservations', 'ReservationRequest').objects.get()
        self.assertFalse(reservation.handled)
        self.assertEqual(reservation.admin_notes, '')

    def test_public_cannot_read_or_modify_requests(self):
        self.assertEqual(self.client.get(self.endpoint).status_code, 405)
        self.assertIn(self.client.get(self.endpoint + '1/').status_code, [404, 405])
        self.assertIn(self.client.patch(self.endpoint + '1/', {}, format='json').status_code, [404, 405])

    def test_admin_requires_login_and_displays_saved_request_to_staff(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        url = reverse('admin:reservations_reservationrequest_changelist')
        self.assertEqual(self.client.get(url).status_code, 302)
        admin = get_user_model().objects.create_superuser('test-admin', 'admin@example.com', 'test-only-admin-password')
        self.client.force_login(admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'visitor@example.com')
        self.assertContains(response, '+12025550123')

    def test_public_submission_is_rate_limited(self):
        responses = [self.post() for _ in range(6)]
        self.assertEqual([r.status_code for r in responses], [201, 201, 201, 201, 201, 429])

    def test_view_only_staff_cannot_mark_requests_handled(self):
        self.assertEqual(self.post().status_code, 201)
        reservation = apps.get_model('reservations', 'ReservationRequest').objects.get()
        viewer = get_user_model().objects.create_user('viewer', is_staff=True)
        viewer.user_permissions.add(Permission.objects.get(codename='view_reservationrequest'))
        self.client.force_login(viewer)
        self.client.post(reverse('admin:reservations_reservationrequest_changelist'), {
            'action': 'mark_handled', '_selected_action': [reservation.pk],
        })
        reservation.refresh_from_db()
        self.assertFalse(reservation.handled)
