from django.db.models import Q, F
from django.db import models
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import date
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .forms import AdvertItemForm, AdvertImageFormSet, DonationProofForm
from .models import ProjectDonation
from django.contrib import messages
from .models import CommunityPolicy
from .models import (
    WellWishes,
    CDA, Levy, UserLevy, Payment, ExecutiveMember, Defaulter,
    Event, CommunityInfo, NavbarImage, PaidMember, Committee, CommitteeMember,
    CommitteeToDo, CommitteeAchievement, AdvertCategory, AdvertItem, AdvertImage,
    Artisan, Professional, ProjectDonation, ProjectImage, DonationProof, Proposal, ProjectDonationModal,
    BirthdayCelebrant, Banner, SpecialDonation,
    ArtisanImage, ProfessionalImage # Ensure these are imported if used directly, though prefetch_related is usually enough
)


from django.shortcuts import redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from .models import CustomUser
from .utils import send_approval_email

def get_project_donation_modal_context():
    try:
        modal_content = ProjectDonationModal.objects.first()
    except ProjectDonationModal.DoesNotExist:
        modal_content = None
    return {'project_donation_modal': modal_content}

def get_site_settings():
    return SiteSetting.objects.first()

from .models import BirthdayWish

def birthday_wish_view(request, wish_id):
    wish = get_object_or_404(BirthdayWish, pk=wish_id)
    context = {
        'wish': wish
    }
    return render(request, 'cda_app/birthday_wish_template.html', context)

from django.contrib.auth import get_user_model
from .models import CustomUser
""" from .forms import AdvertItemForm, AdvertImageFormSet, DonationProofForm """
from .forms import ( CustomUserCreationForm, CustomAuthenticationForm, AdvertItemForm, AdvertImageFormSet, DonationProofForm, RegularLevyForm, WellWishesForm)

from .utils import (
    send_registration_email,
    send_approval_email,
    send_advert_created_email,
    send_advert_approved_email,
    send_donation_proof_email,
    send_birthday_email,
    send_defaulter_email
)
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

""" from .models import (
    CDA, UserProfile, Levy, UserLevy, Payment, ExecutiveMember, 
    Event, CommunityInfo, NavbarImage, PaidMember, Committee,
    CommitteeMember, CommitteeToDo, CommitteeAchievement,
    AdvertCategory, AdvertItem, AdvertImage, Artisan,
    Professional, ProjectDonation, ProjectImage, DonationProof, Proposal
) """

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_portal/dashboard.html')

@login_required
@user_passes_test(is_admin)
def admin_user_management(request):
    User = get_user_model()  # This will get your custom user model
    users = User.objects.all().order_by('-date_joined')
    search_query = request.GET.get('q', '')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query))
    
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_portal/user_management.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(is_admin)
def admin_approve_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)
    user.is_approved = True
    user.is_active = True
    user.save()
    send_approval_email(user)
    messages.success(request, f"User {user.username} has been approved.")
    return redirect('admin_user_management')

@login_required
@user_passes_test(is_admin)
def admin_advert_approval(request):
    adverts = AdvertItem.objects.filter(is_approved=False).order_by('-published_date')
    return render(request, 'admin_portal/advert_approval.html', {'adverts': adverts})

@login_required
@user_passes_test(is_admin)
def admin_approve_advert(request, advert_id):
    advert = get_object_or_404(AdvertItem, pk=advert_id)
    advert.is_approved = True
    advert.save()
    send_advert_approved_email(advert)
    messages.success(request, f"Advert '{advert.title}' has been approved.")
    return redirect('admin_advert_approval')

@login_required
@user_passes_test(is_admin)
def admin_reject_advert(request, advert_id):
    advert = get_object_or_404(AdvertItem, pk=advert_id)
    advert.delete()
    messages.success(request, f"Advert '{advert.title}' has been rejected and deleted.")
    return redirect('admin_advert_approval')


from .utils import send_birthday_email, get_project_donation_modal_context
from .forms import WellWishesForm

def home(request):
    today = timezone.now().date()

    # Fetch active banners for left and right positions
    # Using .first() to get a single instance or None
    left_banner = Banner.objects.filter(position='left', is_active=True).first()
    right_banner = Banner.objects.filter(position='right', is_active=True).first()
    
    executive_members = ExecutiveMember.objects.all()
    committees = Committee.objects.all()
    upcoming_events = Event.objects.all().order_by('date')
    community_info = CommunityInfo.objects.all().order_by('-published_date')
    defaulters = Defaulter.objects.all()
    paid_members = PaidMember.objects.all().order_by('-payment_date')
    left_image = NavbarImage.objects.filter(position='left').first()
    right_image = NavbarImage.objects.filter(position='right').first()
    project_donations = ProjectDonation.objects.all().prefetch_related('images')
    special_donations = SpecialDonation.objects.all().order_by('-donation_date')

    # Fetch the latest BirthdayWish object
    birthday_wish_frame = BirthdayWish.objects.order_by('-id').first() # Or filter by date if needed

    selected_cda = request.GET.get('cda', '').strip()
    selected_debt_for = request.GET.get('debt_for', '').strip()

    if selected_cda:
        defaulters = defaulters.filter(cda__iexact=selected_cda)
    if selected_debt_for:
        defaulters = defaulters.filter(title_defaulted__iexact=selected_debt_for)

    # ✅ Always show celebrants whose birthday is today
    birthday_celebrants = BirthdayCelebrant.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day
    )

    # ➕ Show upcoming birthday countdown
    next_birthday = BirthdayCelebrant.objects.exclude(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day
    ).order_by(
        'date_of_birth__month', 'date_of_birth__day'
    ).first()

    days_until_next = None
    if next_birthday:
        next_date = next_birthday.date_of_birth.replace(year=today.year)
        if next_date < today:
            next_date = next_date.replace(year=today.year + 1)
        days_until_next = (next_date - today).days

    if request.method == 'POST':
        sender_name = request.POST.get('sender_name')
        message = request.POST.get('message')
        celebrant_id = request.POST.get('celebrant_id')

        if sender_name and message and celebrant_id:
            celebrant = get_object_or_404(BirthdayCelebrant, id=celebrant_id)

            WellWishes.objects.create(
                celebrant=celebrant,
                sender_name=sender_name,
                message=message
            )

            # ✅ Send birthday email and mark as celebrated ONCE per day
            if celebrant.user and celebrant.last_celebrated_year != today.year:
                send_birthday_email(celebrant.user)
                celebrant.last_celebrated_year = today.year
                celebrant.save()

            messages.success(request, 'Your well wish has been submitted and birthday email sent!')
            return redirect('home')
    else:
        form = WellWishesForm()

    context = {
        'executive_members': executive_members,
        'committees': committees,
        'upcoming_events': upcoming_events,
        'community_info': community_info,
        'defaulters': defaulters,
        'paid_members': paid_members,
        'left_image': left_image,
        'right_image': right_image,
        'cdas': Defaulter.cda_choices,
        'debt_for_choices': Defaulter.debt_for_choices,
        'selected_cda': selected_cda,
        'selected_debt_for': selected_debt_for,
        'project_donations': project_donations,
        'special_donations': special_donations,
        'birthday_wish_frame': birthday_wish_frame,
        'left_banner': left_banner,
        'right_banner': right_banner,
        'left_image': left_image,
        'right_image': right_image,
        'project_donation_modal': get_project_donation_modal_context()['project_donation_modal'],
        'well_wishes_form': WellWishesForm(),
    }

    context.update(get_project_donation_modal_context())
    return render(request, 'home.html', context)

@login_required
def community_policy_view(request):
    policies = CommunityPolicy.objects.all().order_by('-published_date')
    context = {
        'policies': policies
    }
    return render(request, 'community_policy.html', context)


@login_required
def reply_to_wish(request, wish_id):
    wish = get_object_or_404(WellWishes, id=wish_id)
    
    if request.method == 'POST':
        reply_message = request.POST.get('reply_message')
        if reply_message:
            # Here you could create a Reply model instance or handle it differently
            # For now, we'll just show a success message
            messages.success(request, f'Your reply to {wish.sender_name} has been sent.')
            return redirect('home')
    
    messages.error(request, 'Invalid reply request')
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Added request.FILES for image upload
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate user until approved
            user.save()            
            # Send registration confirmation email
            send_registration_email(user)            
            # Show success message
            messages.success(request, 'Your registration was successful! Please check your email for confirmation and wait for admin approval.')            
            return redirect('registration_pending')  # Redirect to pending approval page
            
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration.html', {'form': form})


def registration_pending(request):
    return render(request, 'registration_pending.html')

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account is inactive. Please contact an administrator.')
                elif not user.is_approved:
                    messages.error(request, 'Your account is awaiting admin approval. Please wait for approval.')
                else:
                    login(request, user)
                    next_url = request.POST.get('next', request.GET.get('next', ''))
                    if next_url:
                        return redirect(next_url)
                    return redirect('home')
            else:
                messages.error(request, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
    else:
        form = CustomAuthenticationForm()
    
    # Pass the 'next' parameter to the template
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {
        'form': form,
        'next': next_url
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

# cda_app/views.py
from datetime import datetime, timedelta
from django.db.models import Sum
from .models import RegularLevy

@login_required
def profile(request):
    # Regular Levies/Dues (current and recent)
    regular_levies = RegularLevy.objects.filter(
        user=request.user,
        status__in=['unpaid', 'pending', 'rejected']
    ).order_by('-year', '-month')
    
    # Payment History (paid levies)
    payment_history = RegularLevy.objects.filter(
        user=request.user,
        status='paid'
    ).order_by('-updated_at')
    
    # Outstanding Levies (grouped by payment_for)
    three_months_ago = timezone.now() - timedelta(days=90)
    outstanding = RegularLevy.objects.filter(
        user=request.user,
        status__in=['unpaid', 'pending', 'rejected'],
        created_at__lte=three_months_ago
    )
    
    outstanding_levies = {}
    for category in dict(RegularLevy.PAYMENT_FOR_CHOICES).keys():
        category_levies = outstanding.filter(payment_for=category)
        if category_levies.exists():
            total_amount = category_levies.aggregate(Sum('amount'))['amount__sum']
            outstanding_levies[category] = {
                'total_amount': total_amount,
                'count': category_levies.count()
            }
    
    return render(request, 'profile.html', {
        'user': request.user,
        'regular_levies': regular_levies,
        'payment_history': payment_history,
        'outstanding_levies': outstanding_levies
    })


@login_required
def upload_regular_levy_proof(request, levy_id):
    levy = get_object_or_404(RegularLevy, id=levy_id, user=request.user)
    if request.method == 'POST':
        form = RegularLevyForm(request.POST, request.FILES, instance=levy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proof of payment uploaded successfully.')
            return redirect('profile')  # Redirect to user profile or a confirmation page
        else:
            messages.error(request, 'Error uploading proof of payment. Please check the form.')
    else:
        form = RegularLevyForm(instance=levy)
    return render(request, 'upload_proof.html', {'form': form, 'levy': levy})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import RegularLevy
from .utils import send_payment_proof_email
import logging

logger = logging.getLogger(__name__)

@login_required
def upload_payment_proof(request):
    if request.method == 'POST' and request.FILES.get('proof_image'):
        try:
            # Validate file size
            if request.FILES['proof_image'].size > settings.MAX_UPLOAD_SIZE:
                return JsonResponse({
                    'success': False,
                    'error': 'File size must be less than 5MB'
                }, status=400)
                
            levy_id = request.POST.get('levy_id')
            category = request.POST.get('category')
            
            if levy_id:
                # Handle single levy payment
                levy = get_object_or_404(RegularLevy, id=levy_id, user=request.user)
                levy.proof_of_payment = request.FILES['proof_image']
                levy.status = 'pending'
                levy.save()
                
                send_payment_proof_email(levy, request.user)
                return JsonResponse({
                    'success': True,
                    'message': 'Payment proof submitted! Status updated to Pending.',
                    'new_status': 'pending',
                    'levy_id': levy.id
                })
                
            elif category:
                # Handle category payment
                levies = RegularLevy.objects.filter(
                    user=request.user,
                    payment_for=category,
                    status__in=['unpaid', 'pending', 'rejected']
                )
                
                if not levies.exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'No unpaid levies found for {category}'
                    }, status=400)
                
                updated_count = 0
                for levy in levies:
                    levy.proof_of_payment = request.FILES['proof_image']
                    levy.status = 'pending'
                    levy.save()
                    updated_count += 1
                    send_payment_proof_email(levy, request.user)
                    
                return JsonResponse({
                    'success': True,
                    'message': f'Payment proof uploaded for {updated_count} items!',
                    'new_status': 'pending',
                    'category': category
                })
                
        except Exception as e:
            logger.error(f"Error uploading payment proof: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing your payment'
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method or missing proof image'
    }, status=400)

def send_payment_proof_email(levy, user):
    subject = 'Payment Proof Uploaded'
    html_message = render_to_string('emails/payment_proof_uploaded.html', {
        'levy': levy,
        'user': user
    })
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )
    
# cda_app/views.py
from .forms import CustomUserChangeForm, CustomPasswordChangeForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            profile_form = CustomUserChangeForm(instance=request.user)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')
        else:
            profile_form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
            password_form = CustomPasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile was successfully updated!')
                return redirect('profile')
    else:
        profile_form = CustomUserChangeForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'edit_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

def events(request):
    all_events = Event.objects.all().order_by('date')
    return render(request, 'events.html', {'all_events': all_events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_detail.html', {'event': event})

@login_required
def committee_detail(request, committee_id):
    committee = get_object_or_404(Committee, pk=committee_id)
    members = CommitteeMember.objects.filter(committee=committee)
    todos = CommitteeToDo.objects.filter(committee=committee)
    achievements = CommitteeAchievement.objects.filter(committee=committee)
    context = {
        'committee': committee,
        'members': members,
        'todos': todos,
        'achievements': achievements,
    }
    return render(request, 'committee_detail.html', context)

@login_required
def pay_levy(request, levy_id):
    if request.method == 'POST':
        user_levy = UserLevy.objects.get(id=levy_id, user=request.user)
        notes = request.POST.get('notes', '')
        # Simulate payment success
        Payment.objects.create(user_levy=user_levy, amount_paid=user_levy.amount_due, notes=notes)
        user_levy.is_paid = True
        user_levy.save()
    return redirect('profile')


@staff_member_required
def resend_approval_email_admin(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    send_approval_email(user, admin_user=request.user)
    messages.success(request, f"Approval email resent to {user.username}.")
    return redirect(f"/admin/cda_app/customuser/{user_id}/change/")


def advert_list(request):
    category_name = request.GET.get('category')
    user_filter = request.GET.get('user')
    
    if category_name:
        advert_items = AdvertItem.objects.filter(is_approved=True, category=category_name).order_by('-published_date')
    elif user_filter and request.user.is_authenticated:
        advert_items = AdvertItem.objects.filter(is_approved=True, user=request.user).order_by('-published_date')
    else:
        advert_items = AdvertItem.objects.filter(is_approved=True).order_by('-published_date')

    context = {
        'advert_items': advert_items
    }
    return render(request, 'advert_list.html', context)

def advert_detail(request, pk):
    advert_item = get_object_or_404(AdvertItem, pk=pk)
    return render(request, 'advert_detail.html', {'advert_item': advert_item})

def submit_proposal(request, advert_id):
    if request.method == 'POST':
        advert = get_object_or_404(AdvertItem, pk=advert_id)
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        proposed_amount = request.POST.get('proposed_amount')
        notes = request.POST.get('notes', '')
        
        Proposal.objects.create(
            advert=advert,
            name=name,
            email=email,
            phone_number=phone_number,
            proposed_amount=proposed_amount,
            notes=notes
        )
        
        messages.success(request, 'Your Negotiated Proposal is submitted successfully. Kindly wait patiently while the advertiser will communicate with you. Thank you')
        return redirect('advert_detail', pk=advert_id)
    return redirect('home')

@login_required
def proposal_list(request):
    proposals = Proposal.objects.filter(advert__user=request.user).order_by('-created_at')
    return render(request, 'proposal_list.html', {'proposals': proposals})


@login_required
def create_advert(request):
    if request.method == 'POST':
        form = AdvertItemForm(request.POST, request.FILES)
        formset = AdvertImageFormSet(request.POST, request.FILES, queryset=AdvertImage.objects.none())
        print(f"Debug: Form is valid: {form.is_valid()}")
        print(f"Debug: Form errors: {form.errors}")
        print(f"Debug: Formset is valid: {formset.is_valid()}")
        print(f"Debug: Formset errors: {formset.errors}")
        if form.is_valid() and formset.is_valid():
            advert_item = form.save(commit=False)
            advert_item.user = request.user
            advert_item.is_approved = False  # Set to False for admin approval
            advert_item.save()
            print(f"Debug: Formset cleaned data: {formset.cleaned_data}")
            for image_data in formset.cleaned_data:
                # Check if the formset data is not empty and not marked for deletion
                if image_data and not image_data.get('DELETE', False):
                    image = image_data.get('image')
                    is_main = image_data.get('is_main', False)
                    if image:
                        AdvertImage.objects.create(advert_item=advert_item, image=image, is_main=is_main)
            send_advert_created_email(advert_item)
            return redirect('advert_detail', pk=advert_item.pk)
    else:
        form = AdvertItemForm()
        formset = AdvertImageFormSet(queryset=AdvertImage.objects.none())
    return render(request, 'create_advert.html', {'form': form, 'formset': formset})

@login_required
def artisans_list(request):
    job_title_query = request.GET.get('job_title', '')
    artisans = Artisan.objects.all().prefetch_related('gallery_images')

    if job_title_query:
        artisans = artisans.filter(job_title__icontains=job_title_query)

    context = {
        'artisans': artisans,
        'job_title_query': job_title_query
    }
    return render(request, 'artisans_list.html', context)

@login_required
def professionals_list(request):
    job_title_query = request.GET.get('job_title', '')
    professionals = Professional.objects.all().prefetch_related('gallery_images')

    if job_title_query:
        professionals = professionals.filter(job_title__icontains=job_title_query)

    context = {
        'professionals': professionals,
        'job_title_query': job_title_query
    }
    return render(request, 'professionals_list.html', context)

""" @login_required
def artisan_gallery_view(request, artisan_id):
    artisan = get_object_or_404(Artisan.objects.prefetch_related('gallery_images'), pk=artisan_id)
    return render(request, 'artisan_gallery.html', {'artisan': artisan}) """

""" @login_required
def professional_gallery_view(request, professional_id):
    professional = get_object_or_404(Professional.objects.prefetch_related('gallery_images'), pk=professional_id)
    return render(request, 'professional_gallery.html', {'professional': professional}) """

@login_required
def artisan_gallery_view(request, artisan_id):
    # Prefetch gallery images to load them efficiently
    artisan = get_object_or_404(Artisan.objects.prefetch_related('gallery_images'), pk=artisan_id)
    context = {
        'artisan': artisan
    }
    return render(request, 'artisan_gallery.html', context)

@login_required
def professional_gallery_view(request, professional_id):
    # Prefetch gallery images to load them efficiently
    professional = get_object_or_404(Professional.objects.prefetch_related('gallery_images'), pk=professional_id)
    context = {
        'professional': professional
    }
    return render(request, 'professional_gallery.html', context)

@login_required
def project_donations_list(request):
    project_donations = ProjectDonation.objects.all().prefetch_related('images')
    return render(request, 'project_donations_list.html', {'project_donations': project_donations})

def past_executives(request):
    past_members = ExecutiveMember.objects.filter(end_date__lt=timezone.now()).order_by('-start_date')
    context = {
        'executive_members': past_members,
        'title': 'Past Executive Members'
    }
    return render(request, 'executive_members.html', context)

def present_executives(request):
    present_members = ExecutiveMember.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now()).order_by('start_date')
    context = {
        'executive_members': present_members,
        'title': 'Present Executive Members'
    }
    return render(request, 'executive_members.html', context)


from django.views.generic import ListView
from django.db.models.functions import ExtractMonth, ExtractDay

class BirthdayCalendarView(ListView):
    model = BirthdayCelebrant
    template_name = 'birthday_calendar.html'
    context_object_name = 'birthdays'
    
    def get_queryset(self):
        return BirthdayCelebrant.objects.annotate(
            month=ExtractMonth('date_of_birth'),
            day=ExtractDay('date_of_birth')
        ).order_by('month', 'day')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        birthdays = self.get_queryset()
        birthdays_by_month = {month: [] for month in range(1, 13)}
        for birthday in birthdays:
            birthdays_by_month[birthday.month].append(birthday)
        context['birthdays_by_month'] = birthdays_by_month
        today = timezone.now().date()
        context['today_month'] = today.month
        context['today_day'] = today.day
        return context

@login_required
def upload_donation_proof(request, donation_id):
    project_donation = get_object_or_404(ProjectDonation, pk=donation_id)
    if request.method == 'POST':
        form = DonationProofForm(request.POST, request.FILES)
        if form.is_valid():
            donation_proof = form.save(commit=False)
            donation_proof.project_donation = project_donation
            donation_proof.save()
            send_donation_proof_email(donation_proof)
            return redirect('project_donations_list')  # Redirect to the donations list after successful upload
    else:
        form = DonationProofForm(initial={'donation_reference_number': project_donation.reference_number})
    return render(request, 'upload_donation_proof.html', {'form': form, 'project_donation': project_donation})


from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ContactMessage
from django.http import JsonResponse



def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message_text = request.POST.get("message")

        # Save message to DB
        contact_msg = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message_text
        )

        # Send email notification to admin
        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message_text}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Admin email
        )

        # If request is AJAX -> return JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Thank you! Your message has been sent."})

        # Else normal form flow
        messages.success(request, "Thank you! Your message has been sent.")
        return redirect("home")

    return render(request, "contact.html")  # fallback if GET
