from django.apps import AppConfig


class Tahmin90AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tahmin90app'

    def ready(self):
        import tahmin90app.signals
