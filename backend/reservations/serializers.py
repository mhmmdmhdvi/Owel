import re

from rest_framework import serializers

from .models import ReservationRequest


class ReservationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationRequest
        fields = ['full_name', 'email', 'whatsapp']
        extra_kwargs = {
            field: {'error_messages': {
                'required': 'این قسمت را تکمیل کنید.',
                'blank': 'این قسمت را تکمیل کنید.',
                'invalid': 'مقدار واردشده معتبر نیست.',
            }} for field in fields
        }

    def validate_full_name(self, value):
        if any(ord(character) < 32 for character in value):
            raise serializers.ValidationError('نام را بدون نویسه‌های کنترلی وارد کنید.')
        return value

    def validate_whatsapp(self, value):
        digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
        normalized = re.sub(r'[\s()\-]', '', value.translate(digits))
        if normalized.startswith('00'):
            normalized = '+' + normalized[2:]
        if not re.fullmatch(r'\+[1-9][0-9]{7,14}', normalized):
            raise serializers.ValidationError('شماره واتس‌اپ را همراه کد کشور وارد کنید، مانند ‎+12025550123.')
        return normalized

    # Formatted numbers may exceed the normalized model field's 16 characters.
    whatsapp = serializers.CharField(max_length=40, trim_whitespace=True, error_messages={
        'required': 'شماره واتس‌اپ را وارد کنید.',
        'blank': 'شماره واتس‌اپ را وارد کنید.',
    })
