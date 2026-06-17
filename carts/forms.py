from django import forms
from .models import ProformaInvoice
from accounts.models import Account
from accounts.data import AREA_CODE
from django.core.validators import EmailValidator


from django import forms
from .models import ProformaInvoice

# class ProformaInvoiceForm(forms.ModelForm):
#     recipient_mobile_area = forms.ChoiceField(
#         choices=AREA_CODE,  # Assumes AREA_CODE is imported/defined globally
#         initial='',
#         required=False      # Handled dynamically in __init__
#     )
#     delivery_note = forms.CharField(
#         required=False,
#         widget=forms.Textarea(attrs={
#             'placeholder': '配送備註 | Delivery Note',
#             'class': 'w-full textarea textarea-primary placeholder:text-xs w-full max-h-24'
#         })
#     )
#     do_not_send_invoice = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={'class': 'toggle toggle-xs toggle-primary'})
#     )
#     recipient_email = forms.EmailField(
#         required=False,
#         widget=forms.EmailInput(attrs={
#             'class': 'grow w-full placeholder:text-xs bg-transparent',
#             'placeholder': 'recipient@example.com｜收件人電子郵件',
#         })
#     )
#     gift_message = forms.CharField(
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'textarea textarea-bordered w-full text-xs max-h-24',
#             'rows': '3',
#             'placeholder': 'Write your gift message here...｜請在此填寫您的祝福字句...',
#         })
#     )
#     save_to_address_book = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={'class': 'toggle toggle-xs toggle-accent'})
#     )

#     class Meta:
#         model = ProformaInvoice
#         fields = [
#             'email', 'recipient_first_name', 'recipient_last_name', 
#             'recipient_mobile_area', 'recipient_mobile_number', 
#             'address_line_1', 'address_line_2', 'city', 'state_province_region', 
#             'country', 'postal_code', 'delivery_note', 'do_not_send_invoice',
#             'google_place_id', 'latitude', 'longitude', 'is_verified_by_google',
#             'recipient_email', 'gift_message', 'save_to_address_book'
#         ]

#     def __init__(self, *args, **kwargs):
#         display_mode = kwargs.pop('display_mode', 'PHYSICAL')
#         super().__init__(*args, **kwargs)

#         # Standardise Class Injectors
#         standard_fields = {
#             "recipient_first_name": "First Name｜名字",
#             "recipient_last_name": "Last Name｜姓氏",
#             "email": "contact email｜聯繫郵箱",
#             "recipient_mobile_number": "123456789",
#             "address_line_2": "Address2｜地址2",
#             "city": "City｜城市",
#             "state_province_region": "State/Province｜州/縣/省",
#             "country": "Country/Region｜國家/地區",
#             "postal_code": "Post Code｜郵編/郵遞區號"
#         }
#         for field, placeholder in standard_fields.items():
#             self.fields[field].widget.attrs.update({
#                 "class": "grow w-full placeholder:text-xs",
#                 "placeholder": placeholder
#             })
        
#         self.fields["recipient_mobile_area"].widget.attrs.update({
#             "class": "select rounded-l-[0.5rem] grow w-[6rem] validator"
#         })
#         self.fields["address_line_1"].widget.attrs.update({
#             "id": "id_address_line_1",
#             "class": "grow w-full placeholder:text-xs autocomplete-input",
#         })

#         # Hide Google Autocomplete Coordinates
#         for f in ['google_place_id', 'latitude', 'longitude', 'is_verified_by_google']:
#             self.fields[f].widget = forms.HiddenInput()
#             self.fields[f].required = False

#         # Set Required Settings Symmetrically
#         self.fields['email'].required = True
        
#         if display_mode in ["PHYSICAL", "PHYSICAL_AND_VOUCHER"]:
#             for f in ['recipient_first_name', 'recipient_last_name', 'recipient_mobile_area', 'recipient_mobile_number', 'address_line_1']:
#                 self.fields[f].required = True
#             self.fields['recipient_email'].required = (display_mode == "PHYSICAL_AND_VOUCHER")
#         else:
#             for f in ['recipient_first_name', 'recipient_last_name', 'recipient_mobile_area', 'recipient_mobile_number', 'address_line_1', 'city', 'state_province_region', 'country']:
#                 self.fields[f].required = False
#             self.fields['recipient_email'].required = (display_mode == "VOUCHER_ONLY")

#         # Readonly locks for prefilled locations
#         for field_name in ['address_line_1', 'address_line_2', 'city', 'state_province_region', 'country']:
#             if self.initial.get(field_name):
#                 self.fields[field_name].widget.attrs['readonly'] = True
#                 curr = self.fields[field_name].widget.attrs.get('class', '')
#                 self.fields[field_name].widget.attrs['class'] = f"{curr} bg-base-200 pointer-events-none select-none text-neutral-500"

#     def clean(self):
#         cleaned_data = super().clean()
#         if self.fields['address_line_1'].required and not cleaned_data.get("address_line_1"):
#             self.add_error('address_line_1', "Shipping address line 1 is missing.")
#         if self.fields['recipient_email'].required and not cleaned_data.get("recipient_email"):
#             self.add_error('recipient_email', "Voucher recipient email is missing.")
#         return cleaned_data
    

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
            'email': forms.EmailInput(attrs={'id': 'id_email', 'class': 'grow font-mono text-xs font-semibold', 'placeholder': 'Email ｜ 常用電子郵件'}),
            'recipient_first_name': forms.TextInput(attrs={'id': 'id_recipient_first_name', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': '*First Name ｜ 名字'}),
            'recipient_last_name': forms.TextInput(attrs={'id': 'id_recipient_last_name', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': '*Last Name ｜ 姓氏'}),
            'recipient_mobile_number': forms.TextInput(attrs={'id': 'id_recipient_mobile_number', 'class': 'grow join-item text-xs font-mono font-semibold', 'placeholder': 'Phone ｜ 手機號碼'}),
            
            'address_line_1': forms.TextInput(attrs={'id': 'id_address_line_1', 'class': 'grow font-sans text-xs font-semibold'}),
            'address_line_2': forms.TextInput(attrs={'id': 'id_address_line_2', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': 'Address 2 (Apt, Suite, Floor) ｜ 樓層、門牌（選填）'}),
            'city': forms.TextInput(attrs={'id': 'id_city', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': 'City ｜ 城市'}),
            'state_province_region': forms.TextInput(attrs={'id': 'id_state_province_region', 'class': 'grow font-sans text-xs font-semibold', 'placeholder': 'State / Region ｜ 省份/州'}),
            'country': forms.Select(attrs={'id': 'id_country', 'class': 'select select-sm select-ghost font-sans text-xs font-bold -ml-3 bg-transparent border-0 focus:outline-none focus:ring-0'}),
            'postal_code': forms.TextInput(attrs={'id': 'id_postal_code', 'class': 'grow font-mono text-xs font-semibold', 'placeholder': 'ZIP Code ｜ 郵遞區號'}),
            
            'recipient_email': forms.EmailInput(attrs={'id': 'id_recipient_email', 'class': 'grow font-mono text-xs font-semibold', 'placeholder': "Recipient's Email ｜ 收件人電子郵件"}),
            'gift_message': forms.Textarea(attrs={'id': 'id_gift_message', 'class': 'textarea textarea-bordered w-full text-xs font-medium font-sans h-20 min-h-0', 'placeholder': 'May all beings be happy and free... ｜ 願一切眾生常得安樂...'}),
            'delivery_note': forms.Textarea(attrs={'id': 'id_delivery_note', 'class': 'textarea textarea-bordered w-full text-xs font-medium font-sans h-20 min-h-0', 'placeholder': 'Instructions for shop/courier... ｜ 給店家的備註備忘...'}),
            'do_not_send_invoice': forms.CheckboxInput(attrs={'id': 'id_do_not_send_invoice', 'class': 'checkbox checkbox-primary checkbox-xs'}),
        }

    def __init__(self, *args, **kwargs):
        """
        🔒 HIGH-SECURITY DYNAMIC ADAPTATION CONSTRUCTOR:
        Alters standard field mandatory validation parameters dynamically based 
        on the required checkout display mode structure.
        """
        self.display_mode = kwargs.pop('display_mode', 'PHYSICAL')
        super().__init__(*args, **kwargs)

        if self.display_mode in ['EPRODUCT_ONLY', 'VOUCHER_ONLY']:
            if 'country' in self.fields:
                self.fields.pop('country')
            if 'state_province_region' in self.fields:
                self.fields.pop('state_province_region')

        if self.display_mode in ['VOUCHER_ONLY', 'PHYSICAL_AND_VOUCHER']:
            self.fields['recipient_email'].required = True  # 🌟 Forces validation lock!
            if not any(isinstance(v, EmailValidator) for v in self.fields['recipient_email'].validators):
                self.fields['recipient_email'].validators.append(EmailValidator())                

        # 1. Strip default required configurations completely
        for field in self.fields.values():
            field.required = False
        
        # 2. Re-apply strict mandatory locks surgically based on display conditions
        self.fields['email'].required = True # Buyer email channel is globally required

        if self.display_mode in ['PHYSICAL', 'PHYSICAL_AND_VOUCHER']:
            self.fields['recipient_first_name'].required = True
            self.fields['recipient_last_name'].required = True
            self.fields['recipient_mobile_area'].required = True
            self.fields['recipient_mobile_number'].required = True
            self.fields['address_line_1'].required = True
            self.fields['city'].required = True
            self.fields['state_province_region'].required = True
            self.fields['country'].required = True

        # if self.display_mode in ['VOUCHER_ONLY', 'PHYSICAL_AND_VOUCHER']:
        #     self.fields['recipient_email'].required = True
        #     self.fields['recipient_email'].validators.append(EmailValidator())
        if self.display_mode in ['VOUCHER_ONLY', 'PHYSICAL_AND_VOUCHER']:
            self.fields['recipient_email'].required = True
            # Safe application using the confirmed import hook
            if not any(isinstance(v, EmailValidator) for v in self.fields['recipient_email'].validators):
                self.fields['recipient_email'].validators.append(EmailValidator())

    # 🎯 FIX 2: Intercept form validation and explicitly inject the properties onto the instance 
    # This prevents the model-level 'blank=False' rule from tripping up over an absent value
    def clean(self):
        return super().clean()