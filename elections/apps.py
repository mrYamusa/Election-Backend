# elections/apps.py
from django.apps import AppConfig

class ElectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elections'  # Make sure this matches your app's name

    def ready(self):
        import elections.signals  # Ensure the signals are imported