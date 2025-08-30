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



from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CdaAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cda_app"
    verbose_name = _("CDA App")

    def ready(self):
        from django.contrib import admin
        from .models import ContactMessage

        # Add ContactMessage count to Jazzmin dashboard
        def contact_message_count():
            return ContactMessage.objects.count()

        # Register in admin site index template
        admin.site.site_header = "Madandola Estate Admin"
