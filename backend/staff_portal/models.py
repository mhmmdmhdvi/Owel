import uuid

from django.conf import settings
from django.db import models


class LoginGuard(models.Model):
    key = models.CharField(max_length=64, unique=True)
    username = models.CharField(max_length=150)
    failures = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class TelegramConnection(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telegram_user_id = models.BigIntegerField(unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_username()


class PortalSession(models.Model):
    token_digest = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auth_hash = models.CharField(max_length=64)
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TelegramUpdate(models.Model):
    update_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TelegramDelivery(models.Model):
    dedupe_key = models.CharField(max_length=120, unique=True)
    chat_id = models.BigIntegerField()
    kind = models.CharField(max_length=20, choices=[('reservation', 'Reservation'), ('menu', 'Menu'), ('stopped', 'Stopped')])
    connection = models.ForeignKey(TelegramConnection, on_delete=models.SET_NULL, null=True, blank=True)
    reservation = models.ForeignKey('reservations.ReservationRequest', on_delete=models.CASCADE, null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(db_index=True)
    lease_until = models.DateTimeField(null=True, blank=True)
    lease_id = models.UUIDField(default=uuid.uuid4)
    sent_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'pk']
