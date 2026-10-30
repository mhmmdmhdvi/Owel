from rest_framework import serializers

from reservations.models import ReservationRequest


class StaffLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=1024, trim_whitespace=False, write_only=True)
    telegram_init_data = serializers.CharField(max_length=10000, required=False, allow_blank=True, trim_whitespace=False)


class ReservationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationRequest
        fields = ['id', 'full_name', 'email', 'whatsapp', 'created_at', 'handled']


class ReservationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationRequest
        fields = ['id', 'full_name', 'email', 'whatsapp', 'created_at', 'handled', 'admin_notes']
        read_only_fields = ['id', 'full_name', 'email', 'whatsapp', 'created_at']
