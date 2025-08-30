from django import forms
from .models import CommunityInfo

from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser, CDA, AdvertItem, AdvertImage, AdvertMessage, DonationProof
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    cda = forms.ModelChoiceField(
        queryset=CDA.objects.all(),
        required=False,
        empty_label="Select CDA",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                'phone_number', 'user_type', 'cda', 'image',
                'password1', 'password2', 'captcha')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user
    
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    password = None  # Remove the password field from the form
    cda = forms.ModelChoiceField(
        queryset=CDA.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'user_type', 'cda', 'image')
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.cda:
            self.initial['cda'] = CDA.objects.filter(name=self.instance.cda).first()
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['cda']:
            user.cda = self.cleaned_data['cda'].name
        else:
            user.cda = None
        if commit:
            user.save()
        return user

from django.contrib.auth.forms import PasswordChangeForm
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class AdvertItemForm(forms.ModelForm):
    class Meta:
        model = AdvertItem
        fields = ['category', 'title', 'description', 'amount', 'location', 'condition', 'phone_number']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number (e.g., +2348012345678)'}),
        }

class AdvertImageForm(forms.ModelForm):
    class Meta:
        model = AdvertImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

AdvertImageFormSet = inlineformset_factory(AdvertItem, AdvertImage, form=AdvertImageForm, extra=5, max_num=5, can_delete=False)

class AdvertMessageForm(forms.ModelForm):
    class Meta:
        model = AdvertMessage
        fields = ['name', 'phone_number', 'willing_amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone Number'}),
            'willing_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your Willing Amount'}),
        }

class DonationProofForm(forms.ModelForm):
    class Meta:
        model = DonationProof
        fields = ['donator_name', 'whatsapp_number', 'donated_amount', 'payment_receipt_image', 'donation_reference_number']
        widgets = {
            'donator_name': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'donated_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_receipt_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'donation_reference_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }


from .models import RegularLevy, WellWishes

class RegularLevyForm(forms.ModelForm):
    class Meta:
        model = RegularLevy
        fields = ['user', 'month', 'year', 'payment_for', 'amount', 'cda', 'status', 'proof_of_payment']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_for': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'cda': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'proof_of_payment': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class WellWishesForm(forms.ModelForm):
    class Meta:
        model = WellWishes
        fields = ['celebrant', 'sender_name', 'message']
        widgets = {
            'celebrant': forms.HiddenInput(), # This will be set dynamically
        }
        

from django_ckeditor_5.widgets import CKEditor5Widget

class MyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))


class CommunityInfoForm(forms.ModelForm):
    class Meta:
        model = CommunityInfo
        fields = '__all__'
        widgets = {
            'title': CKEditor5Widget(config_name='default'),
            'content': CKEditor5Widget(config_name='default'),
        }

from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import SiteSettings

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'footer_text': CKEditor5Widget(config_name='default'),
        }
