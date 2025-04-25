#core/urls.py
from django.urls import path
from .views import DashboardView, CustomPasswordResetConfirmView

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
]
