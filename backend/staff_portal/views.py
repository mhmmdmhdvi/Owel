import hashlib
import math
import secrets
from datetime import timedelta

from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from reservations.models import ReservationRequest
from .authentication import CanViewReservations, PortalAuthentication
from .models import PortalSession, TelegramConnection
from .serializers import ReservationDetailSerializer, ReservationListSerializer, StaffLoginSerializer
from .telegram_auth import bind_telegram, verify_init_data


class LoginThrottle(AnonRateThrottle):
    rate = '20/minute'


class StaffLoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = StaffLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        raw = values.get('telegram_init_data', '')
        identity = verify_init_data(raw) if raw else None
        user = authenticate(request, username=values['username'], password=values['password'])
        if user is None:
            locked = getattr(request, 'login_locked_until', None)
            if locked:
                remaining = max(1, math.ceil((locked - timezone.now()).total_seconds()))
                return Response({'detail': 'ورود موقتاً قفل شد. پس از پایان زمان دوباره تلاش کنید.', 'retry_after': remaining}, status=429, headers={'Retry-After': str(remaining)})
            return Response({'detail': 'نام کاربری یا رمز عبور معتبر نیست.'}, status=401)
        if not user.is_staff or not user.has_perm('reservations.view_reservationrequest'):
            raise PermissionDenied('این حساب اجازه دسترسی به درخواست‌ها را ندارد.')
        if identity is not None:
            bind_telegram(user, identity)
        token = secrets.token_urlsafe(32)
        session = PortalSession.objects.create(
            token_digest=hashlib.sha256(token.encode()).hexdigest(), user=user,
            auth_hash=user.get_session_auth_hash(), telegram_user_id=identity,
            expires_at=timezone.now() + timedelta(hours=8),
        )
        return Response({'token': token, 'expires_at': session.expires_at.isoformat(), 'user': {
            'username': user.get_username(),
            'can_change': user.has_perm('reservations.change_reservationrequest'),
            'telegram_connected': TelegramConnection.objects.filter(user=user, active=True).exists(),
        }})


class StaffAPIView(APIView):
    authentication_classes = [PortalAuthentication]
    permission_classes = [CanViewReservations]
    parser_classes = [JSONParser]


class StaffLogoutView(StaffAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationListView(StaffAPIView):
    def get(self, request):
        queryset = ReservationRequest.objects.all()
        query = request.query_params.get('q', '').strip()[:200]
        if query:
            queryset = queryset.filter(Q(full_name__icontains=query) | Q(email__icontains=query) | Q(whatsapp__icontains=query))
        state = request.query_params.get('status', 'all')
        if state in ['new', 'handled']:
            queryset = queryset.filter(handled=state == 'handled')
        page = Paginator(queryset, 20).get_page(request.query_params.get('page', '1')[:8])
        return Response({
            'results': ReservationListSerializer(page.object_list, many=True).data,
            'count': page.paginator.count, 'page': page.number, 'pages': page.paginator.num_pages,
            'can_change': request.user.has_perm('reservations.change_reservationrequest'),
        })


class ReservationDetailView(StaffAPIView):
    def get(self, request, pk):
        return Response(ReservationDetailSerializer(get_object_or_404(ReservationRequest, pk=pk)).data)

    def patch(self, request, pk):
        if not request.user.has_perm('reservations.change_reservationrequest'):
            raise PermissionDenied('اجازه ویرایش ندارید.')
        reservation = get_object_or_404(ReservationRequest, pk=pk)
        serializer = ReservationDetailSerializer(reservation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
