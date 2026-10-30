import hashlib
import unicodedata
from datetime import timedelta

from django.contrib.auth.backends import ModelBackend
from django.db import transaction
from django.utils import timezone

from .models import LoginGuard


class GuardedModelBackend(ModelBackend):
    """Serialize attempts per username so concurrent requests cannot bypass lockout."""

    @transaction.atomic
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not isinstance(username, str) or not isinstance(password, str):
            return None
        username = unicodedata.normalize('NFKC', username).strip()
        key = hashlib.sha256(username.encode()).hexdigest()
        LoginGuard.objects.get_or_create(key=key, defaults={'username': username[:150]})
        guard = LoginGuard.objects.select_for_update().get(key=key)
        now = timezone.now()
        if guard.locked_until and guard.locked_until > now:
            if request is not None:
                request.login_locked_until = guard.locked_until
            return None
        if guard.locked_until:
            guard.failures = 0
            guard.locked_until = None
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is not None:
            guard.failures = 0
            guard.locked_until = None
        else:
            guard.failures += 1
            if guard.failures >= 3:
                guard.locked_until = now + timedelta(minutes=15)
                if request is not None:
                    request.login_locked_until = guard.locked_until
        guard.save(update_fields=['failures', 'locked_until', 'updated_at'])
        return user
