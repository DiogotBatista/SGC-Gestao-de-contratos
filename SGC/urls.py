# SGC/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    # Adm do Django
    path("painel_admin/", admin.site.urls),
    # App Core
    path("", include("core.urls")),
    # App contratos
    path("contratos/", include("contratos.urls")),
    # App reuniões
    path("atas/", include("reunioes.urls")),
    # App dashboards
    path("dashboards/", include("dashboards.urls")),
    # URLs de autenticação:
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # App notaspessoais
    path("notaspessoais/", include("notaspessoais.urls")),
    # App tarefas
    path("tarefas/", include("tarefas.urls")),
    # App Propostas
    path("propostas/", include("propostas.urls")),
    # App medicoes
    path("medicoes/", include("medicoes.urls")),
    # Senhas
    path("senhas/", include("senhas.urls")),
    # frota
    path("frota/", include("frota.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
