from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from datetime import datetime, date
from django_ckeditor_5.fields import CKEditor5Field


""" from ckeditor_uploader.fields import RichTextUploadingField """
""" import datetime """


class CDA(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    

""" from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cda = models.ForeignKey(CDA, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')
    
    def __str__(self):
        return self.user.username """
    

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ]
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')
    cda = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # Add this field
    last_approval_email_sent = models.DateTimeField(null=True, blank=True)
    objects = UserManager()
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class ApprovalLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_logs')
    email_sent_to = models.EmailField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_emails_sent')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Approval Email Log"
        verbose_name_plural = "Approval Email Logs"

    def __str__(self):
        return f"Approval email to {self.email_sent_to} on {self.sent_at.strftime('%Y-%m-%d %H:%M')}"


class ProjectDonationModal(models.Model):
    title = CKEditor5Field(config_name='default', blank=True, null=True)
    content = CKEditor5Field(config_name='default')
    image = models.ImageField(upload_to='project_donation_images/', blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class BirthdayCelebrant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='celebrant_images/')
    date_of_birth = models.DateField()
    admin_wishes = CKEditor5Field(config_name='default')
    last_celebrated_year = models.IntegerField(null=True, blank=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if isinstance(self.last_celebrated_year, (datetime, date)):
                self.last_celebrated_year = self.last_celebrated_year.year
            elif isinstance(self.last_celebrated_year, str) and self.last_celebrated_year.isdigit():
                self.last_celebrated_year = int(self.last_celebrated_year)
        except Exception as e:
            pass  # or log this
        super().save(*args, **kwargs)

    def is_birthday_today(self):
        today = datetime.now().date()
        return self.date_of_birth.month == today.month and self.date_of_birth.day == today.day

    class Meta:
        verbose_name = "Birthday Celebrant"
        verbose_name_plural = "Birthday Celebrants"



from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"



class WellWishes(models.Model):
    celebrant = models.ForeignKey(BirthdayCelebrant, on_delete=models.CASCADE, related_name='well_wishes')
    sender_name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wish for {self.celebrant.name} from {self.sender_name}"

    class Meta:
        verbose_name = "Well Wish"
        verbose_name_plural = "Well Wishes"
        ordering = ['-created_at']
        
        
class WellWishReply(models.Model):
    wish = models.ForeignKey(WellWishes, on_delete=models.CASCADE, related_name='replies')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Well Wish Replies'
    
    def __str__(self):
        return f"Reply to {self.wish.sender_name} by {self.sender.username}"

class Levy(models.Model):
    CDA_CHOICES = [
        ('Unity CDA', 'Unity CDA'),
        ('Harmony CDA', 'Harmony CDA'),
        ('Valley-View CDA', 'Valley-View CDA'),
    ]
    LEVY_TYPE_CHOICES = [
        ('Development Fees', 'Development Fees'),
        ('Others', 'Others'),
        ('Electricity', 'Electricity'),
        ('Security Fees', 'Security Fees'),
    ]

    cda = models.ForeignKey(CDA, on_delete=models.CASCADE, null=True, blank=True, help_text="Leave blank for joint payments (Electricity, Security Fees)")
    levy_type = models.CharField(max_length=50, choices=LEVY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.levy_type} - {self.amount}"

class UserLevy(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    levy = models.ForeignKey(Levy, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.levy.levy_type} - Due: {self.amount_due}"

class Payment(models.Model):
    user_levy = models.ForeignKey(UserLevy, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment by {self.user_levy.user.username} for {self.user_levy.levy.levy_type}"


class ExecutiveMember(models.Model):
    cda = models.ForeignKey(CDA, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='executive_members/', blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"


class SpecialDonation(models.Model):
    title = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, unique=True)
    donator_name = models.CharField(max_length=255)
    donated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_image = models.ImageField(upload_to='special_donation_receipts/', blank=True, null=True)
    donation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.donator_name}"

    class Meta:
        verbose_name = "Special Donation"
        verbose_name_plural = "Special Donations"
        ordering = ['-donation_date']

class Defaulter(models.Model):
    image = models.ImageField(upload_to='defaulter_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    cda_choices = [
        ('Unity CDA', 'Unity CDA'),
        ('Harmony CDA', 'Harmony CDA'),
        ('Valley-View CDA', 'Valley-View CDA'),
    ]
    cda = models.CharField(max_length=100, choices=cda_choices, verbose_name="CDA")
    amount_indebted = models.DecimalField(max_digits=10, decimal_places=2)
    debt_for_choices = [
        ('Security Fees', 'Security Fees'),
        ('Electricity', 'Electricity'),
        ('Development Levy', 'Development Levy'),
        ('Others', 'Others'),
    ]
    title_defaulted = models.CharField(max_length=200, choices=debt_for_choices, verbose_name="Debt For:")
    status_choices = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('In Progress', 'In Progress'),
        ('Indebt', 'Indebt'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='Pending')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.title_defaulted}"

class Event(models.Model):
    title = CKEditor5Field(config_name='default', blank=True, null=True)
    date = models.DateField()
    time = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=200)
    description = CKEditor5Field(config_name='default')
    """ description = models.TextField() """
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} on {self.date}"

class CommunityInfo(models.Model):
    title = CKEditor5Field(config_name='default', blank=True, null=True)
    content = CKEditor5Field(config_name='default')
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Community Info"

    def __str__(self):
        return self.title

class NavbarImage(models.Model):
    POSITION_CHOICES = [
        ('left', 'Left Corner'),
        ('right', 'Right Corner'),
    ]
    image = models.ImageField(upload_to='navbar_images/')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Navbar Image ({self.position})"

class PaidMember(models.Model):
    image = models.ImageField(upload_to='paid_member_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    cda_choices = [
        ('Unity CDA', 'Unity CDA'),
        ('Harmony CDA', 'Harmony CDA'),
        ('Valley-View CDA', 'Valley-View CDA'),
    ]
    cda = models.CharField(max_length=100, choices=cda_choices, verbose_name="CDA")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purpose_choices = [
        ('Security Fees', 'Security Fees'),
        ('Electricity', 'Electricity'),
        ('Development Levy', 'Development Levy'),
        ('Others', 'Others'),
    ]
    purpose_of_payment = models.CharField(max_length=200, choices=purpose_choices, verbose_name="Purpose of Payment")
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.amount_paid} ({self.purpose_of_payment})"


class Committee(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = CKEditor5Field(config_name='default', blank=True, null=True)
    roles_responsibilities = CKEditor5Field(config_name='default', blank=True, null=True)

    def __str__(self):
        return self.name

class CommitteeMember(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    image = models.ImageField(upload_to='committee_members/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.committee.name}"

class CommitteeToDo(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='todos')
    task = CKEditor5Field(config_name='default', blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.task} ({self.committee.name})"

class CommitteeAchievement(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='achievements')
    title = CKEditor5Field(config_name='default', blank=True, null=True)
    description = CKEditor5Field(config_name='default', blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.committee.name})"

class AdvertCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ProjectDonation(models.Model):
    title = CKEditor5Field(config_name='default', blank=True, null=True)
    description = CKEditor5Field(config_name='default', blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2)
    reference_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    beneficiary = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title

class ProjectImage(models.Model):
    project = models.ForeignKey(ProjectDonation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')

    def __str__(self):
        return f"Image for {self.project.title}"

class DonationProof(models.Model):
    project_donation = models.ForeignKey(ProjectDonation, on_delete=models.CASCADE, related_name='donation_proofs')
    donator_name = models.CharField(max_length=100)
    whatsapp_number = models.CharField(max_length=20)
    donated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_receipt_image = models.ImageField(upload_to='donation_proofs/')
    donation_reference_number = models.CharField(max_length=100, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.project_donation.title} by {self.donator_name}"

class AdvertItem(models.Model):
    CATEGORY_CHOICES = [
        ('For Sale', 'For Sale'),
        ('For Rent', 'For Rent'),
        ('For Lease', 'For Lease'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    published_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.title

class AdvertImage(models.Model):
    advert_item = models.ForeignKey(AdvertItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='advert_images/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.advert_item.title}"

class Proposal(models.Model):
    advert = models.ForeignKey(AdvertItem, on_delete=models.CASCADE, related_name='proposals')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal for {self.advert.title} by {self.name}"

class AdvertMessage(models.Model):
    advert = models.ForeignKey(AdvertItem, on_delete=models.CASCADE, related_name='messages')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    willing_amount = models.DecimalField(max_digits=10, decimal_places=2)
    message_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.advert.title} from {self.name}"

class Artisan(models.Model):
    # Core Information
    image = models.ImageField(upload_to='artisans/', blank=True, null=True,
                            help_text="Upload a main profile picture for the artisan.")
    name = models.CharField(max_length=100,
                            help_text="Full name of the artisan.")
    job_title = models.CharField(max_length=100,
                                help_text="e.g., Plumber, Electrician, Carpenter.")
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    help_text="Primary phone number for contact.")
    email = models.EmailField(blank=True, null=True,
                            help_text="Email address for business inquiries.")
    
    # Business Details
    location = models.CharField(max_length=200, blank=True, null=True,
                                help_text="Physical location or service area.")
    business_description = CKEditor5Field(config_name='default', blank=True, null=True,
                                            help_text="A brief description of their business.")
    products_services = CKEditor5Field(config_name='default', blank=True, null=True,
                                        help_text="Detailed list of products/services offered.")
    working_hours = models.CharField(max_length=200, blank=True, null=True,
                                    help_text="e.g., Mon-Fri: 9 AM - 5 PM, Sat: 10 AM - 2 PM.")
    
    # Rating and Reviews (for star preview)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0,
                                help_text="Average rating based on reviews (e.g., 4.5).")
    num_reviews = models.IntegerField(default=0,
                                        help_text="Total number of reviews received.")

    class Meta:
        verbose_name = "Artisan"
        verbose_name_plural = "Artisans"
        ordering = ['name'] # Order by name by default

    def __str__(self):
        return f"{self.name} ({self.job_title})"

class ArtisanImage(models.Model):
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='gallery_images',
                                help_text="The artisan this image belongs to.")
    image = models.ImageField(upload_to='artisan_galleries/',
                                help_text="Upload an image for the artisan's gallery.")
    description = models.CharField(max_length=255, blank=True, null=True,
                                    help_text="Optional description for the image.")

    class Meta:
        verbose_name = "Artisan Gallery Image"
        verbose_name_plural = "Artisan Gallery Images"
        ordering = ['id'] # Order by ID for consistent display

    def __str__(self):
        return f"Image for {self.artisan.name}"


class Professional(models.Model):
    # Core Information
    image = models.ImageField(upload_to='professionals/', blank=True, null=True,
                                help_text="Upload a main profile picture for the professional.")
    name = models.CharField(max_length=100,
                            help_text="Full name of the professional.")
    job_title = models.CharField(max_length=100,
                                help_text="e.g., Accountant, Lawyer, Architect.")
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    help_text="Primary phone number for contact.")
    email = models.EmailField(blank=True, null=True,
                                help_text="Email address for business inquiries.")
    
    # Business Details
    location = models.CharField(max_length=200, blank=True, null=True,
                                help_text="Physical location or service area.")
    business_description = CKEditor5Field(config_name='default', blank=True, null=True,
                                            help_text="A brief description of their professional service.")
    products_services = CKEditor5Field(config_name='default', blank=True, null=True,
                                        help_text="Detailed list of services offered.")
    working_hours = models.CharField(max_length=200, blank=True, null=True,
                                    help_text="e.g., Mon-Fri: 9 AM - 5 PM.")
    
    # Rating and Reviews (for star preview)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0,
                                help_text="Average rating based on reviews (e.g., 4.8).")
    num_reviews = models.IntegerField(default=0,
                                        help_text="Total number of reviews received.")

    class Meta:
        verbose_name = "Professional"
        verbose_name_plural = "Professionals"
        ordering = ['name'] # Order by name by default

    def __str__(self):
        return f"{self.name} ({self.job_title})"


class ProfessionalImage(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='gallery_images',
                                        help_text="The professional this image belongs to.")
    image = models.ImageField(upload_to='professional_galleries/',
                                help_text="Upload an image for the professional's gallery.")
    description = models.CharField(max_length=255, blank=True, null=True,
                                    help_text="Optional description for the image.")

    class Meta:
        verbose_name = "Professional Gallery Image"
        verbose_name_plural = "Professional Gallery Images"
        ordering = ['id'] # Order by ID for consistent display

    def __str__(self):
        return f"Image for {self.professional.name}"

# cda_app/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class RegularLevy(models.Model):
    MONTH_CHOICES = [
        ('January', _('January')),
        ('February', _('February')),
        ('March', _('March')),
        ('April', _('April')),
        ('May', _('May')),
        ('June', _('June')),
        ('July', _('July')),
        ('August', _('August')),
        ('September', _('September')),
        ('October', _('October')),
        ('November', _('November')),
        ('December', _('December')),
    ]
    
    PAYMENT_FOR_CHOICES = [
        ('Electricity', _('Electricity')),
        ('Security', _('Security')),
        ('Development Levies', _('Development Levies')),
        ('Sanitations', _('Sanitations')),
        ('Others', _('Others')),
    ]
    
    STATUS_CHOICES = [
        ('unpaid', _('Unpaid')),
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('rejected', _('Rejected')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='levies'
    )
    
    month = models.CharField(
        _('Month'),
        max_length=20,
        choices=MONTH_CHOICES,
        help_text=_('Select the month for this levy')
    )
    
    year = models.PositiveIntegerField(
        _('Year'),
        help_text=_('Enter the year for this levy')
    )
    
    payment_for = models.CharField(
        _('Payment For'),
        max_length=50,
        choices=PAYMENT_FOR_CHOICES,
        help_text=_('Select the purpose of this payment')
    )
    
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Enter the amount to be paid')
    )
    
    cda = models.CharField(
        _('CDA'),
        max_length=100,
        help_text=_('Community Development Association')
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='unpaid',
        help_text=_('Current payment status')
    )
    
    proof_of_payment = models.ImageField(
        _('Proof of Payment'),
        upload_to='payment_proofs/',
        null=True,
        blank=True,
        help_text=_('Upload proof of payment'),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Regular Levy')
        verbose_name_plural = _('Regular Levies')
        ordering = ['-year', '-month']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'month', 'year', 'payment_for'],
                name='unique_user_levy_per_month'
            )
        ]

    def __str__(self):
        return f"{self.get_month_display()} {self.year} - {self.get_payment_for_display()} ({self.user.username})"

    def clean(self):
        """Validate model fields before saving"""
        errors = {}
        
        # Validate year is reasonable (2000-current year + 1)
        current_year = timezone.now().year
        if self.year < 2000 or self.year > current_year + 1:
            errors['year'] = _('Year must be between 2000 and %(current)s') % {'current': current_year + 1}
        
        # Validate amount is positive
        if self.amount <= 0:
            errors['amount'] = _('Amount must be positive')
        
        # Validate payment proof when status is pending/paid
        if self.status in ['pending', 'paid'] and not self.proof_of_payment:
            errors['proof_of_payment'] = _('Proof of payment is required for this status')
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Custom save method with validation and auto-fields"""
        # Auto-fill CDA if not provided
        if not self.cda and hasattr(self.user, 'cda'):
            self.cda = self.user.cda
        
        # Run full validation before saving
        self.full_clean()
        
        # Set timestamps
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)

    def get_status_color(self):
        """Helper method to get status color for UI"""
        status_colors = {
            'unpaid': 'danger',
            'pending': 'warning',
            'paid': 'success',
            'rejected': 'secondary'
        }
        return status_colors.get(self.status, 'info')

    @property
    def is_overdue(self):
        """Check if the levy is overdue (unpaid and past current month)"""
        if self.status != 'unpaid':
            return False
            
        current_date = timezone.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Get month number from month name
        month_number = list(dict(self.MONTH_CHOICES).keys()).index(self.month) + 1
        
        return (self.year < current_year) or \
                (self.year == current_year and month_number < current_month)
                
                
from django.db import models

class FooterSetting(models.Model):
    footer_text = models.TextField(help_text="Text to display in the footer")
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    tiktok_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Footer Setting"
        verbose_name_plural = "Footer Settings"

    def __str__(self):
        return "Footer Configuration"

class SocialMedia(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter (X)'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
    ]
    
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField()
    
    def __str__(self):
        return f"{self.platform.title()}"

    class Meta:
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"
        
        
class SocialMediaLinks(models.Model):
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Social Media Links"

    class Meta:
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"


class FooterText(models.Model):
    content = models.TextField()

    def __str__(self):
        return "Footer Text"


# models.py
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

class SiteSettings(models.Model):
    footer_text = CKEditor5Field(config_name='default')
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    tiktok_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Site Settings"

# Create your models here.

from django.db import models

class BirthdayWish(models.Model):
    logo = models.ImageField(upload_to='birthday_wishes/logos/', blank=True, null=True)
    image = models.ImageField(upload_to='birthday_wishes/images/', blank=True, null=True)
    heading = models.CharField(max_length=255, default="Happy Birthday")
    # Calendar details can be stored as text or a specific date field if needed
    # For now, let's assume it's part of the dynamic text content or handled via a date field
    birth_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=255)
    wishes_text = models.TextField()
    frame_background = models.ImageField(upload_to='birthday_wishes/backgrounds/', blank=True, null=True)

    def __str__(self):
        return f"Birthday Wish for {self.name}"


class CommunityPolicy(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Text', config_name='extends')
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Community Policies"

    def __str__(self):
        return self.title






class Banner(models.Model):
    """
    Model for advertisement banners displayed on the homepage.
    """
    POSITION_CHOICES = [
        ('left', 'Left Sidebar'),
        ('right', 'Right Sidebar'),
        # You could add 'top', 'bottom', 'main_content_area' if needed in the future
    ]

    title = models.CharField(max_length=200, help_text="Short title for the banner (e.g., 'Discount Offer').")
    image = models.ImageField(upload_to='banners/',
                              help_text="Upload the banner image.")
    target_url = models.URLField(max_length=500, blank=True, null=True,
                                 help_text="Optional: URL to navigate to when the banner is clicked (e.g., a product page).")
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, unique=True,
                                help_text="Where this banner will be displayed on the page. Only one banner per position.")
    is_active = models.BooleanField(default=True,
                                    help_text="Check to make this banner active and visible on the site.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Banner"
        verbose_name_plural = "Website Banners"
        ordering = ['position']

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"

    def clean(self):
        # Ensure only one active banner per position
        if self.is_active and Banner.objects.filter(position=self.position, is_active=True).exclude(pk=self.pk).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError(f"An active banner already exists for the '{self.get_position_display()}' position. Please deactivate it first or choose a different position.")

