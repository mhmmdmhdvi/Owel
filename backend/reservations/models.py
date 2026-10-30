from django.db import models


class ReservationRequest(models.Model):
    full_name = models.CharField('نام و نام خانوادگی', max_length=120)
    email = models.EmailField('ایمیل')
    whatsapp = models.CharField('شماره واتس‌اپ', max_length=16)
    created_at = models.DateTimeField('زمان ثبت', auto_now_add=True, db_index=True)
    handled = models.BooleanField('بررسی شده', default=False, db_index=True)
    admin_notes = models.TextField('یادداشت داخلی', blank=True, max_length=2000)

    class Meta:
        ordering = ['-created_at', '-pk']
        verbose_name = 'درخواست رزرو'
        verbose_name_plural = 'درخواست‌های رزرو'

    def __str__(self):
        return self.full_name
