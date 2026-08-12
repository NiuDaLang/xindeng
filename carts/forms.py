from django import forms
from .models import ProformaInvoice
from accounts.models import Account
from accounts.data import AREA_CODE
from django.core.validators import EmailValidator
from .utils import validate_email_mx_domain

from django import forms
from .models import ProformaInvoice

class ProformaInvoiceForm(forms.ModelForm):
    # Declare extra presentation widgets with clean unified configuration matrices
    recipient_mobile_area = forms.ChoiceField(
        choices=AREA_CODE,
        initial='+86',
        required=False,
        widget=forms.Select(attrs={'class': 'select select-bordered join-item font-semibold text-xs tabular-nums focus:ring-0 focus:outline-none'})
    )
    
    # Secure geographical coordinate placeholders absorbing Google Map metadata updates
    google_place_id = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_google_place_id'}))
    latitude = forms.DecimalField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_latitude'}))
    longitude = forms.DecimalField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_longitude'}))
    is_verified_by_google = forms.BooleanField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_is_verified_by_google'}))

    save_to_address_book = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'toggle toggle-xs toggle-accent'}))

    class Meta:
        model = ProformaInvoice
        fields = [
            'email', 'recipient_first_name', 'recipient_last_name', 
            'recipient_mobile_area', 'recipient_mobile_number',
            'address_line_1', 'address_line_2', 'city', 
            'state_province_region', 'country', 'postal_code', 
            'recipient_email', 'gift_message', 'delivery_note', 
            'do_not_send_invoice', 'google_place_id', 'latitude', 
            'longitude', 'is_verified_by_google', 'save_to_address_book'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'id': 'id_email', 'class': 'grow font-mono text-xs font-semibold', 'placeholder': 'Email｜常用電子郵件'}),
            'recipient_first_name': forms.TextInput(attrs={'id': 'id_recipient_first_name', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': '*First Name｜名字'}),
            'recipient_last_name': forms.TextInput(attrs={'id': 'id_recipient_last_name', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': '*Last Name｜姓氏'}),
            'recipient_mobile_number': forms.TextInput(attrs={'id': 'id_recipient_mobile_number', 'class': 'grow join-item text-xs font-mono font-semibold', 'placeholder': 'Phone｜手機號碼'}),
            
            'address_line_1': forms.TextInput(attrs={'id': 'id_address_line_1', 'class': 'grow font-sans text-xs font-semibold'}),
            'address_line_2': forms.TextInput(attrs={'id': 'id_address_line_2', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': 'Address 2 (Apt, Suite, Floor)｜樓層、門牌（選填）'}),
            'city': forms.TextInput(attrs={'id': 'id_city', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': 'City｜城市'}),
            'state_province_region': forms.TextInput(attrs={'id': 'id_state_province_region', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': 'State / Region｜省份/州'}),
            'country': forms.Select(attrs={'id': 'id_country', 'class': 'select select-sm select-ghost font-sans text-xs font-bold -ml-3 bg-transparent border-0 focus:outline-none focus:ring-0'}),
            'postal_code': forms.TextInput(attrs={'id': 'id_postal_code', 'class': 'grow font-mono text-xs font-semibold', 'placeholder': 'ZIP Code｜郵遞區號'}),
            
            'recipient_email': forms.EmailInput(attrs={'id': 'id_recipient_email', 'class': 'grow font-mono text-xs font-semibold', 'placeholder': "Recipient's Email｜收件人電子郵件"}),
            'gift_message': forms.Textarea(attrs={'id': 'id_gift_message', 'class': 'textarea textarea-bordered w-full text-xs font-medium font-sans h-20 min-h-0', 'placeholder': 'May all beings be happy and free...｜願一切眾生常得安樂...'}),
            'delivery_note': forms.Textarea(attrs={'id': 'id_delivery_note', 'class': 'textarea textarea-bordered w-full text-xs font-medium font-sans h-20 min-h-0', 'placeholder': 'Instructions for shop/courier...｜給店家的備註備忘...'}),
            'do_not_send_invoice': forms.CheckboxInput(attrs={'id': 'id_do_not_send_invoice', 'class': 'checkbox checkbox-primary checkbox-xs'}),
        }

    def __init__(self, *args, **kwargs):
        """
        🔒 HIGH-SECURITY DYNAMIC ADAPTATION CONSTRUCTOR:
        """
        self.display_mode = kwargs.pop('display_mode', 'PHYSICAL')
        super().__init__(*args, **kwargs)

        # Step A: Pop elements from the DOM if they are completely unused in digital checkouts
        if self.display_mode in ['EPRODUCT_ONLY', 'VOUCHER_ONLY']:
            self.fields.pop('country', None)
            self.fields.pop('state_province_region', None)

        # Step B: Baseline Reset — Strip absolute defaults to clear space for conditional assignments
        for field in self.fields.values():
            field.required = False
        
        # Step C: Globally Lock Buyer Account Identity Tracking
        if 'email' in self.fields:
            self.fields['email'].required = True

        # Step D: Apply Physical Requirements Surgically
        if self.display_mode in ['PHYSICAL', 'PHYSICAL_AND_VOUCHER']:
            required_physical_fields = [
                'recipient_first_name', 'recipient_last_name', 
                'recipient_mobile_area', 'recipient_mobile_number',
                'address_line_1', 'city', 'state_province_region', 'country'
            ]
            for field_name in required_physical_fields:
                if field_name in self.fields:
                    self.fields[field_name].required = True

        # Step E: Apply Voucher Email Processing Parameters Safely
        if self.display_mode in ['VOUCHER_ONLY', 'PHYSICAL_AND_VOUCHER']:
            if 'recipient_email' in self.fields:
                self.fields['recipient_email'].required = True
                if not any(isinstance(v, EmailValidator) for v in self.fields['recipient_email'].validators):
                    self.fields['recipient_email'].validators.append(EmailValidator())

    def clean(self):
        return super().clean()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email_mx_domain(email)
        return email
