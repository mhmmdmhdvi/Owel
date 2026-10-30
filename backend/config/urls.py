from django.contrib import admin
from django.urls import path
from reservations.views import ReservationRequestCreateView
from staff_portal.views import StaffLoginView, StaffLogoutView, ReservationListView, ReservationDetailView
from staff_portal.webhook import telegram_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/reservations/', ReservationRequestCreateView.as_view(), name='reservation-create'),
    path('api/staff/login/', StaffLoginView.as_view()),
    path('api/staff/logout/', StaffLogoutView.as_view()),
    path('api/staff/reservations/', ReservationListView.as_view()),
    path('api/staff/reservations/<int:pk>/', ReservationDetailView.as_view()),
    path('api/telegram/webhook/', telegram_webhook),
]
