from django.contrib import admin

from .models import ReservationRequest


@admin.register(ReservationRequest)
class ReservationRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'whatsapp', 'created_at', 'handled']
    list_filter = ['handled', 'created_at']
    search_fields = ['full_name', 'email', 'whatsapp']
    readonly_fields = ['created_at']
    fields = ['full_name', 'email', 'whatsapp', 'created_at', 'handled', 'admin_notes']
    list_per_page = 25
    actions = ['mark_handled']

    @admin.action(description='علامت‌گذاری به‌عنوان بررسی‌شده', permissions=['change'])
    def mark_handled(self, request, queryset):
        queryset.update(handled=True)


admin.site.site_header = 'مدیریت اووِل'
admin.site.site_title = 'اووِل'
admin.site.index_title = 'مدیریت سایت'
