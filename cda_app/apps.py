from django.apps import AppConfig

class CdaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cda_app'
    
    def ready(self):
        import cda_app.templatetags.custom_filters  # noqa
        import cda_app.templatetags.batch_filter
        
# cda_app/apps.py
from django.apps import AppConfig
import os

class CdaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cda_app'

    def ready(self):
        media_root = os.path.join(os.path.dirname(__file__), '../../media')
        os.makedirs(media_root, exist_ok=True)
        os.makedirs(os.path.join(media_root, 'payment_proofs'), exist_ok=True)