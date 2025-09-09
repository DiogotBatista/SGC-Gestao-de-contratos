from django.apps import AppConfig


class FrotaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "frota"
    verbose_name = "Frota"

    def ready(self):
        # registra sinais
        from . import signals  # noqa
