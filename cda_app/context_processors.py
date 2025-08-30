""" from .models import Committee

def committees(request):
    return {'committees': Committee.objects.all()} """
    
    
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Committee, AdvertItem  # Adjust this as needed


from django.db.models import Q

def committees(request):
    return {'committees': Committee.objects.all()}

def admin_counts(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'pending_users_count': User.objects.filter(is_active=False).count(),
            'pending_adverts_count': AdvertItem.objects.filter(is_approved=False).count(),
            'total_users_count': User.objects.count(),
        }
    return {}

from .models import FooterSetting

def footer_settings(request):
    settings = FooterSetting.objects.first()
    return {'footer_settings': settings}


from .models import SocialMedia

def social_links(request):
    return {
        'social_links': {item.platform: item.url for item in SocialMedia.objects.all()}
    }
    

from .models import SiteSettings

def global_footer_data(request):
    site_settings = SiteSettings.objects.first()
    return {
        "site_settings": site_settings
    }
