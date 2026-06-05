from django import forms
from .models import UserProfile, Address
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from .data import AREA_CODE, GENDER, BLOOD, COLOR, LABEL, DESTINATIONS_FOR_INPUT, DESTINATIONS_MAINLAND_CHINA
from PIL import Image
import datetime
from django.core.exceptions import ValidationError



# get user model
from django.contrib.auth import get_user_model
Account = get_user_model()

class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # style
        self.fields["username"].widget.attrs.update({
            "class": "input w-full",
            "placeholder": "Username｜用戶名"
        }) 

        self.fields["email"].widget.attrs.update({
            "class": "input w-full",
            "placeholder": "Email｜郵箱",
            "autofocus": False,
        })

        self.fields["receive_newsletter"].widget.attrs.update({
            "class": "checkbox checkbox-xs checkbox-accent",
        })

        self.fields["password1"].widget.attrs.update({
            "class": "input w-full",
            "placeholder": "Password｜密碼",
        })      

        self.fields["password2"].widget.attrs.update({
            "class": "input w-full",
            "placeholder": "Confirm Password｜確認密碼",
        })

        username = forms.CharField(max_length=50)
        email = forms.CharField(max_length=100)
        password1 = forms.CharField(widget=forms.PasswordInput)
        password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['username', 'email', 'receive_newsletter', 'password1', 'password2']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        return cleaned_data


class ResetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].widget.attrs.update({
            "class": "input w-full",
            "placeholder": "New Password｜新密碼",
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "input w-full",
            "placeholder": "Confirm New Password｜確認新密碼",
        })
    
    class Meta:
        model = Account
        fields = ['password']

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        return cleaned_data


class UserForm(forms.ModelForm):
    mobile_area = forms.ChoiceField(
        choices = AREA_CODE,
        initial='',
        # required=True
    )
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'mobile_area', 'mobile_number', 'receive_newsletter']
        # fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for field in self.fields:
        #     print(f"{field}: {self.fields[field].required}")
        self.fields["mobile_area"].required = False    

        # Other attributes
        self.fields["first_name"].widget.attrs.update({
            "type": "text",
            "class": "grow w-full",
            "placeholder": "First Name｜名",
            "autocomplete": "off",
        })
        self.fields["last_name"].widget.attrs.update({
            "type": "text",
            "class": "grow w-full",
            "placeholder": "Last Name｜姓",
            "autocomplete": "off",
        })
        self.fields["username"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Username｜用戶名",
            "hx-get": "/accounts/check-username/",
            "hx-trigger": "keyup changed delay:500ms, blur",
            "hx-target": "#username-error",
            "hx-sync": "closest form:abort",
        })
        self.fields["email"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Email｜郵箱",
            "readonly": True,
        })
        self.fields["mobile_area"].widget.attrs.update({
            "class": "select rounded-l-[0.5rem] w-[6rem] validator",
        })
        self.fields["mobile_number"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "123456789",
        })
        self.fields["receive_newsletter"].widget.attrs.update({
            "class": "checkbox checkbox-xs checkbox-accent ml-[4px]",
        })

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    def validate_image_size(fieldfile_obj):
        file_extension = fieldfile_obj.name.split(".")[-1].lower()
        megabyte_limit = 1.0
        accepted_formats = ["png", "jpg", "jpeg"]

        # filesize = fieldfile_obj.file.size
        if fieldfile_obj.size > megabyte_limit * 1024 * 1024:
            raise forms.ValidationError(f"Image file size cannot exceed {megabyte_limit}MB｜文檔必須小於{megabyte_limit}MB")
        elif file_extension not in accepted_formats:
            raise forms.ValidationError("Image files(jpeg, jpg, png) only｜僅限圖片文件(jpeg, jpg, png)")
          
    profile_picture = forms.ImageField(
        required=False, 
        validators=[validate_image_size],
        error_messages={"invalid": "f'Image files(jpeg, jpg, png) < {megabyte_limit}MB only｜僅限圖片文件(jpeg, jpg, png) < {megabyte_limit}MB'"}, 
        widget=forms.FileInput
    )

    dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices = GENDER,
        initial='DEFAULT',
        # required=True
    )
    blood_type = forms.ChoiceField(
        choices = BLOOD,
        initial='DEFAULT',
        # required=True
    )
    color = forms.ChoiceField(
        choices = COLOR,
        initial='DEFAULT',
        # required=True
    )

    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'dob', 'gender', 'blood_type', 'color')
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["dob", "gender", "blood_type", "color"]:
            self.fields[field].required = False

        # Inside your Form class __init__:
        today_str = datetime.date.today().strftime('%Y-%m-%d')

        self.fields["profile_picture"].widget.attrs.update({
            "class": "file-input w-full",
            "accept": "image/png, image/jpeg, img/jpg"
        })
        self.fields['dob'].widget.attrs.update({
            "type": "date",
            "max": today_str,
            "class": "grow w-full",
            "placeholder": "Date of Birth｜生日",
        })
        self.fields["gender"].widget.attrs.update({
            "class": "select w-full",
        })
        self.fields["blood_type"].widget.attrs.update({
            "class": "select w-full",
        })
        self.fields["color"].widget.attrs.update({
            "class": "select w-full",
        })


class AddressForm(forms.ModelForm):
    label = forms.ChoiceField(
        choices = LABEL,
        initial='',
    )
    country = forms.ChoiceField(
        choices = DESTINATIONS_FOR_INPUT,
        initial='',
    )
    china_province = forms.ChoiceField(
        choices=[('', '請選擇省份')] + list(DESTINATIONS_MAINLAND_CHINA),
        required=False,
    )

    class Meta:
        model = Address
        fields = (
            'label', 'is_default', 'address_line_1', 'address_line_2', 
            'city', 'state_province_region', 'china_province', 'postal_code', 
            'country', 'google_place_id', 'latitude', 'longitude', 'is_verified_by_google',
        )  

        widgets = {
            'google_place_id': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'is_verified_by_google': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["label"].required = False
        self.fields["address_line_1"].required = False
        self.fields["address_line_2"].required = False
        self.fields["city"].required = False
        # self.fields["state_province_region"].required = False
        self.fields["postal_code"].required = False
        # self.fields["country"].required = False
        self.fields["google_place_id"].required = False
        self.fields["latitude"].required = False
        self.fields["longitude"].required = False

        for field_name in ["state_province_region", "china_province", "country"]:
            self.fields[field_name].required = False
            self.fields[field_name].widget.attrs.pop('required', None)

        self.fields['label'].widget.attrs.update({
            "class": "grow w-full focus:outline-none",
            "placeholder": "窩🪹 | Nest",
        })
        self.fields["is_default"].widget.attrs.update({
            "class": "checkbox checkbox-xs checkbox-accent ml-[4px]",
        })
        self.fields["address_line_1"].widget.attrs.update({
            "class": "grow w-full relative",
            "placeholder": "Address_1｜地址_1",
        })
        self.fields["address_line_2"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Address_2｜地址_2",
        })
        self.fields['city'].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "City｜城市",
        })
        self.fields['state_province_region'].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "State｜州/縣",
        })
        self.fields['china_province'].widget.attrs.update({
            "class": f"grow w-full focus:outline-none {'select-error' if self.errors.get('china_province') else ''}",
            "placeholder": "Province｜省份",
        })
        self.fields['country'].widget.attrs.update({
            "class": "grow w-full focus:outline-none",
            "placeholder": "Country/Region｜國家·地區",
        })
        self.fields['postal_code'].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Zip｜郵編",
        })      

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        address_1 = cleaned_data.get("address_line_1")
        china_province = cleaned_data.get("china_province")
        state_province = cleaned_data.get("state_province_region")
        
        # CORE FIX: If there is no street address, ignore ALL address validation.
        # This allows a blank form to pass even if 'country' has a default value.
        if not address_1 or not address_1.strip():
            return cleaned_data

        # Now we know they ARE providing an address, so we enforce rules:
        if country == 'CN' and not china_province:
            self.add_error('china_province', '請選擇省份 | Please select a province.')
        
        # Optional: If you want to ensure other countries have a state (except Singapore etc.)
        # elif not state_province and country not in ['', 'SG', 'HK']:
        #     self.add_error('state_province_region', 'Required | 必填')

        return cleaned_data
    

class AddressBookForm(AddressForm):
    mobile_area = forms.ChoiceField(
        choices = AREA_CODE,
        initial='',
        required=True
    )
    mobile_number = forms.CharField(
        max_length=40,
        required=True
    )

    class Meta:
        model = Address
        fields = (
            'label', 'is_default', 'recipient_first_name', 'recipient_last_name',
            'mobile_area', 'mobile_number', 'address_line_1', 'address_line_2',
            'city', 'state_province_region', 'postal_code', 'country',
            'google_place_id', 'latitude', 'longitude', 'is_verified_by_google',
        )

        widgets = {
            'google_place_id': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'is_verified_by_google': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["address_line_1"].required = True
        self.fields["address_line_1"].blank = False
        self.fields['address_line_1'].error_messages['required'] = 'Please fill in the street address｜請填寫詳細地址'

        self.fields["country"].required = True
        self.fields["recipient_first_name"].required = True
        self.fields["recipient_last_name"].required = True
        self.fields["mobile_area"].required = True
        self.fields["mobile_number"].required = True

        self.fields["recipient_first_name"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Recipient First Name｜收件人名字",
        })
        self.fields["recipient_last_name"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Recipient Last Name｜收件人姓氏",
        })
        self.fields["mobile_area"].widget.attrs.update({
            "class": "select rounded-l-[0.5rem] w-[6rem] focus:outline-none",
        })
        self.fields["mobile_number"].widget.attrs.update({
            "class": "grow w-full",
            "placeholder": "Mobile Number｜手機號碼",
        })

    def clean_address_line_1(self):
        address = self.cleaned_data.get('address_line_1')
        # strip() handles cases where someone just enters spaces
        if not address or not address.strip():
            raise forms.ValidationError('Please fill in the street address｜請填寫詳細地址')
        return address.strip()
