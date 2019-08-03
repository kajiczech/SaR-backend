from django.apps import AppConfig


class SarConfig(AppConfig):
    name = 'backend.apps.sar'

    def ready(self):
        import backend.apps.sar.signals
