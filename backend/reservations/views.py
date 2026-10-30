from rest_framework import generics, permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.db import transaction
from staff_portal.delivery import queue_reservation

from .serializers import ReservationRequestSerializer


class ReservationRequestCreateView(generics.CreateAPIView):
    serializer_class = ReservationRequestSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [AnonRateThrottle]
    http_method_names = ['post', 'options']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            reservation = serializer.save()
            queue_reservation(reservation)
        return Response({'message': 'درخواست شما ثبت شد.'}, status=status.HTTP_201_CREATED)
