from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import reply_to_wish

urlpatterns = [
    # Admin Portal URLs
    path('admin-portal/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/users/', views.admin_user_management, name='admin_user_management'),
    path('admin-portal/users/approve/<int:user_id>/', views.admin_approve_user, name='admin_approve_user'),
    path('admin-portal/adverts/', views.admin_advert_approval, name='admin_advert_approval'),
    path('admin-portal/adverts/approve/<int:advert_id>/', views.admin_approve_advert, name='admin_approve_advert'),
    path('admin-portal/adverts/reject/<int:advert_id>/', views.admin_reject_advert, name='admin_reject_advert'),
    path('admin/resend-approval-email/<int:user_id>/', views.resend_approval_email_admin, name='resend_approval_email'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('birthday-wish/<int:wish_id>/', views.birthday_wish_view, name='birthday_wish'),
    
    # Existing URLs
    path('', views.home, name='home'),
    path('register/', views.register, name='registration'),
    path('register/pending/', views.registration_pending, name='registration_pending'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/', views.profile, name='profile'),
    path('profile/upload-payment-proof/', views.upload_payment_proof, name='upload_payment_proof'),
    path('levy/<int:levy_id>/upload-proof/', views.upload_regular_levy_proof, name='upload_regular_levy_proof'),    
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('reply-to-wish/<int:wish_id>/', reply_to_wish, name='reply_to_wish'),
    path('pay_levy/<int:levy_id>/', views.pay_levy, name='pay_levy'),
    path('committees/<int:committee_id>/', views.committee_detail, name='committee_detail'),
    path('adverts/', views.advert_list, name='advert_list'),
    path('adverts/<int:pk>/', views.advert_detail, name='advert_detail'),
    path('adverts/create/', views.create_advert, name='create_advert'),
    path('adverts/<int:advert_id>/submit_proposal/', views.submit_proposal, name='submit_proposal'),
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('artisans/', views.artisans_list, name='artisans_list'),
    path('professionals/', views.professionals_list, name='professionals_list'),
    path('artisans/<int:artisan_id>/gallery/', views.artisan_gallery_view, name='artisan_gallery'),
    path('professionals/<int:professional_id>/gallery/', views.professional_gallery_view, name='professional_gallery'),
    
    
    path('project_donations/', views.project_donations_list, name='project_donations_list'),
    path('project_donations/<int:donation_id>/upload_proof/', views.upload_donation_proof, name='upload_donation_proof'),
    path('executives/past/', views.past_executives, name='past_executives'),
    path('executives/present/', views.present_executives, name='present_executives'),
    path('birthdays/', views.BirthdayCalendarView.as_view(), name='birthday_calendar'),
    path('community-policy/', views.community_policy_view, name='community_policy'),
]