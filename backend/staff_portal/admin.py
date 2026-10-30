from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError

from .models import LoginGuard, PortalSession, TelegramConnection, TelegramDelivery


class GuardedAdminForm(AdminAuthenticationForm):
    def get_invalid_login_error(self):
        if getattr(self.request, 'login_locked_until', None):
            return ValidationError('ورود موقتاً قفل شده است. پس از ۱۵ دقیقه دوباره تلاش کنید.', code='locked')
        return super().get_invalid_login_error()


admin.site.login_form = GuardedAdminForm


@admin.register(TelegramConnection)
class TelegramConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_user_id', 'active', 'created_at']
    readonly_fields = ['user', 'telegram_user_id', 'created_at']
    list_filter = ['active']
    actions = ['revoke']

    def has_add_permission(self, request):
        return False

    @admin.action(description='لغو دسترسی تلگرام', permissions=['change'])
    def revoke(self, request, queryset):
        identities = list(queryset.values_list('telegram_user_id', flat=True))
        queryset.update(active=False)
        PortalSession.objects.filter(telegram_user_id__in=identities).delete()


@admin.register(LoginGuard)
class LoginGuardAdmin(admin.ModelAdmin):
    list_display = ['username', 'failures', 'locked_until']
    readonly_fields = ['key', 'username', 'failures', 'locked_until', 'updated_at']
    actions = ['unlock']

    def has_add_permission(self, request):
        return False

    @admin.action(description='بازکردن قفل ورود', permissions=['change'])
    def unlock(self, request, queryset):
        queryset.update(failures=0, locked_until=None)


@admin.register(TelegramDelivery)
class TelegramDeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'kind', 'attempts', 'next_attempt_at', 'sent_at', 'cancelled_at', 'last_error']
    list_filter = ['kind', 'sent_at', 'cancelled_at']
    readonly_fields = [field.name for field in TelegramDelivery._meta.fields]

    def has_add_permission(self, request):
        return False
