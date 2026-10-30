import hashlib

from django.utils import timezone
from django.utils.crypto import constant_time_compare
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from .models import PortalSession, TelegramConnection


class PortalAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts:
            return None
        if len(parts) != 2 or parts[0].lower() != b'bearer' or len(parts[1]) > 128:
            raise AuthenticationFailed('لطفاً دوباره وارد شوید.')
        digest = hashlib.sha256(parts[1]).hexdigest()
        session = PortalSession.objects.select_related('user').filter(token_digest=digest).first()
        if not session:
            raise AuthenticationFailed('لطفاً دوباره وارد شوید.')
        user = session.user
        valid = user.is_active and session.expires_at > timezone.now() and constant_time_compare(session.auth_hash, user.get_session_auth_hash())
        if session.telegram_user_id is not None:
            valid = valid and TelegramConnection.objects.filter(user=user, telegram_user_id=session.telegram_user_id, active=True).exists()
        if not valid:
            session.delete()
            raise AuthenticationFailed('لطفاً دوباره وارد شوید.')
        return user, session


class CanViewReservations(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_active and request.user.is_staff and request.user.has_perm('reservations.view_reservationrequest'))
