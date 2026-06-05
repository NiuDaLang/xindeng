import uuid
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .data import AREA_CODE, GENDER, BLOOD, COLOR, DESTINATIONS_FOR_INPUT, LABEL, CUSTOMER_GROUP
from store.models import Product, ProductVariation
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from datetime import date, timedelta
import random
import string
from decimal import Decimal
from django.db.models import F
from datetime import timedelta
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, receive_newsletter, password=None, **extra_fields):
        if not email:
            raise ValueError("請提供郵箱 | User must have an email address")

        # if not username:
        #     raise ValueError("請提供用戶名 | User must have an username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            receive_newsletter=receive_newsletter,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password, first_name=None, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            receive_newsletter=False,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name          = models.CharField(blank=True, null=True, max_length=50)
    last_name           = models.CharField(blank=True, null=True, max_length=50)
    username            = models.CharField(max_length=50, unique=True)
    email               = models.EmailField(max_length=100, unique=True)
    mobile_area         = models.CharField(blank=True, null=True, max_length=15)
    mobile_number       = models.CharField(blank=True, null=True, max_length=40)
    receive_newsletter  = models.BooleanField(default=True)

    # required
    date_joined         = models.DateTimeField(auto_now_add=True)
    last_login          = models.DateTimeField(auto_now_add=True)
    is_admin            = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=False)
    is_superadmin       = models.BooleanField(default=False)

    USERNAME_FIELD      = "email"
    REQUIRED_FIELDS     = ["username"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    
    @property
    def default_address(self):
        return self.profile.addresses.filter(is_default=True).first()


class UserProfile(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture     = models.ImageField(default="userprofile/default.png", blank=True, upload_to="userprofile")
    dob                 = models.DateField(blank=True, null=True)
    gender              = models.CharField(blank=True, max_length=10, choices=GENDER)
    blood_type          = models.CharField(blank=True, max_length=15, choices=BLOOD)
    color               = models.CharField(blank=True, max_length=15, choices=COLOR)

    def __str__(self):
        return self.user.username

    def get_completion_percentage(self):
        # Define the fields required for full personalization
        account_fields = ['first_name', 'last_name', 'mobile_number']
        profile_fields = ['dob', 'gender', 'profile_picture', 'blood_type', 'color']
        address_fields = ['address_line_1', 'country']

        filled_count = 0
        total_fields = len(account_fields) + len(profile_fields) + len(address_fields)

        for field in account_fields:
            if getattr(self.user, field):
                filled_count += 1

        for field in profile_fields:
            val = getattr(self, field)
            if val: # Checks if it's not None, empty string, or default image
                if field == 'profile_picture' and "default.png" in val.url:
                    continue
                filled_count += 1

        addr = self.addresses.filter(is_default=True).first()
        if addr:
            for field in address_fields:
                if getattr(addr, field):
                    filled_count += 1
        
        if total_fields == 0: return 0

        return int((filled_count / total_fields) * 100)


class Address(models.Model):
    # 1. Ownership & Labeling
    profile                 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')  # This is key for easy lookups
    label                   = models.CharField(max_length=50, choices=LABEL, blank=True, null=True)
    is_default              = models.BooleanField(default=False)
    recipient_first_name    = models.CharField(blank=True, null=True, max_length=50)
    recipient_last_name     = models.CharField(blank=True, null=True, max_length=50)
    mobile_area             = models.CharField(blank=True, null=True, max_length=15)
    mobile_number           = models.CharField(blank=True, null=True, max_length=40)

    # 2. The "Human Readable" Block (Always Required for Manual/Global entry)
    # These are used as the fallback if Google API data is incomplete.
    address_line_1          = models.CharField(max_length=255, blank=True, null=True) # St, Apt, Suite, Landmark
    address_line_2          = models.CharField(max_length=255, blank=True, null=True)
    city                    = models.CharField(max_length=100, blank=True, null=True)
    state_province_region   = models.CharField(max_length=100, blank=True, null=True)
    china_province          = models.CharField(max_length=100, blank=True) # New field
    country                 = models.CharField(max_length=2, choices=DESTINATIONS_FOR_INPUT, default="", blank=False) # ISO 3166-1 alpha-2 (e.g., 'US', 'FR')
    postal_code             = models.CharField(max_length=20, blank=True, null=True) # Optional for global

    # 3. Google API Specifics (Optional/Nullable)
    # If the user uses the Google Autocomplete, these get filled.
    google_place_id         = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    latitude                = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True)
    longitude               = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True)
    
    # 4. Verification Metadata
    is_verified_by_google   = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    last_updated            = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        country = next((t[1] for t in DESTINATIONS_FOR_INPUT if t[0] == self.country), 'Earth')
        fields = [self.address_line_1, self.address_line_2, self.city, self.state_province_region, country, self.postal_code]
        valid_fields = [str(f).strip() for f in fields if f and str(f).strip()]
        return ", ".join(valid_fields)
    
    def save(self, *args, **kwargs):
        # Use an atomic transaction to prevent race conditions
        with transaction.atomic():
            # 1. If this is the account's first address, mark it as default automatically
            if not Address.objects.filter(profile=self.profile).exists():
                self.is_default = True

            # 2. If this address is being set as default, unset all others for this account
            if self.is_default:
                Address.objects.filter(profile=self.profile, is_default=True).update(is_default=False)
            super().save(*args, **kwargs)

    @property
    def full_address(self):
        country = next((t[1] for t in DESTINATIONS_FOR_INPUT if t[0] == self.country), 'Earth')
        fields = [self.address_line_1, self.address_line_2, self.city, self.state_province_region, country, self.postal_code]
        valid_fields = [str(f).strip() for f in fields if f and str(f).strip()]
        return ", ".join(valid_fields)
    

class UserProductList(models.Model):
    LIST_TYPE_CHOICES = (
        ('WISHLIST', '願望清單 | Wishlist'),
        ('FAVORITE', '收藏清單 | Favorite'),
    )
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_lists')
    product_variation   = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, related_name='product_lists')
    list_type           = models.CharField(max_length=10, choices=LIST_TYPE_CHOICES)
    added_date          = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product_variation', 'list_type'],
                name='unique_user_product_variation_list_constraint'
            )
        ]
        verbose_name = 'User_Product_List'
        verbose_name_plural = 'User_Product_Lists'

    def __str__(self):
        return f"{self.user.username}'s {self.list_type} - {self.product_variation}"
    

class Perk(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("percentage", "Percentage Off"),
        ("fixed_amount", "Fixed Amount Off"),
    )

    code                        = models.CharField(max_length=50, unique=True)
    description                 = models.TextField()
    discount_type               = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default="percentage")
    discount_value              = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    featured_image              = models.ImageField(upload_to="perks", blank=True, null=True)
    is_active                   = models.BooleanField(default=True)
    valid_from                  = models.DateTimeField()
    valid_to                    = models.DateTimeField(null=True, blank=True)
    min_spending_requirement    = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    max_uses                    = models.PositiveIntegerField(null=True, blank=True)
    uses_count                  = models.PositiveIntegerField(default=0)
    created_at                  = models.DateTimeField(auto_now_add=True)
    updated_at                  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"code name: {self.code}"
    
    def is_within_validity_period(self):
        now = timezone.now()
        return (
            self.valid_from <= now and
            (self.valid_to is None or self.valid_to >= now) and
            (self.max_uses is None or self.uses_count < self.max_uses)
        )
    
    def has_available_uses(self):
        if self.max_uses is None:
            return True
        return self.uses_count < self.max_uses
    
    @transaction.atomic
    def increment_usage(self):
        """
        Safely increments the uses_count for this perk.
        Refetches the latest data to ensure we haven't hit the limit.
        """
        # Lock the row for update to prevent race conditions
        perk = Perk.objects.select_for_update().get(pk=self.pk)
        if perk.has_available_uses():
            perk.uses_count = F('uses_count') + 1
            perk.save(update_fields=['uses_count'])
            return True
        return False
    
    @property
    def discount_rate(self):
        if self.discount_type == "percentage":
            return f"{self.discount_value}%"
        return f"¥{self.discount_value}"

    @property
    def chinese_disc_rate(self):
        if self.discount_type == "percentage":
            # 1. Calculate remaining (e.g. 100 - 20 = 80.00)
            rate = Decimal('100') - self.discount_value
            
            # 2. Normalize to strip trailing zeros (80.00 -> 80, 87.50 -> 87.5)
            # 3. Use :f to ensure we NEVER get '8E+1' scientific notation
            clean_rate = format(rate.normalize(), 'f')
            
            # 4. Apply Chinese "Zhé" Logic:
            # If it's a multiple of 10 (80, 70, 90), we use the first digit (8, 7, 9)
            # If it's not (85, 87.5), we remove the decimal point (85, 875)
            if float(clean_rate) % 10 == 0 and '.' not in clean_rate:
                final_val = str(int(float(clean_rate) / 10))
            else:
                final_val = clean_rate.replace('.', '')
                
            return f"{final_val}折"
        
        return f"減 ¥{self.discount_value.normalize():f}"

    @property
    def formatted_expiry(self):
        if self.valid_to:
            # %-m and %-d remove leading zeros (e.g., 03 -> 3)
            # Use %m and %d if you prefer 2026-03-31
            return f'Expiry｜有效至 {self.valid_to.strftime("%Y-%-m-%-d")}'
        return "No Expiry｜不限時"
   
    @property
    def split_description(self):
        """Splits by [lg] and returns a dict with fallback"""
        parts = self.description.split('[lg]')
        return {
            'en': parts[0].strip(),
            'cn': parts[1].strip() if len(parts) > 1 else parts[0].strip()
        }

    @property
    def desc_en(self): return self.split_description['en']

    @property
    def desc_cn(self): return self.split_description['cn']

    @property
    def remaining_uses(self):
        if self.max_uses is None:
            return None # Unlimited
        return self.max_uses - self.uses_count
    
    @property
    def safe_min_spending(self):
        return self.min_spending_requirement or 0
    
      
# ####### IMPORTANT ########
# 3. Handling "General Sales" (Non-Member)
# For your general promotions (e.g., XMAS2024), you don't need a UserPerk record. Your checkout logic should check both:
# Is it a Global Code? Search the Perk model directly for the string entered. If found and is_active, apply it.
# Is it a Personal Code? Search the UserPerk model for the numeric code entered. If found, check is_used and the evaluator.
# ####### IMPORTANT ########

class UserPerk(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    perk = models.ForeignKey(Perk, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    # Optional: store a unique code if not using the global perk code
    unique_code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        if self.is_used:
            return f"{self.perk} - used; user_code: {self.unique_code}"
        else:
            return f"{self.perk} - unused; user_code: {self.unique_code}"

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self.generate_numeric_code()
        super().save(*args, **kwargs)

    def generate_numeric_code(self, attempt=1):
        # Format: [PerkID(3 digits)] + [UserID(3 digits)] + Random(6 digits)
        # This ensures the code is numeric and highly likely to be unique
        if attempt > 10:
            raise Exception("Could not generate a unique perk code after 10 attempts.")

        prefix = str(self.perk.id).zfill(3)[:3]
        user_part = str(self.user.id).zfill(3)[:3]
        random_part = ''.join(random.choices(string.digits, k=10))

        code = f"{prefix}{user_part}{random_part}"

        # Collision check
        if UserPerk.objects.filter(unique_code=code).exists():
            return self.generate_numeric_code(attempt + 1) # Retry if exists
        return code
    
    @property
    def personalized_expiry(self):
        code = self.perk.code.upper()

        if "NEW_MEMBER" in code:
            # 30 days from registration
            return self.user.date_joined + timedelta(days=30)
        
        if "BIRTHDAY" in code:
            dob = self.user.profile.dob
            if not dob:
                return None
            today = date.today()
            try:
                this_year_bday = dob.replace(year=today.year)
            except ValueError: # Handle Feb 29th on non-leap years
                this_year_bday = dob.replace(year=today.year, day=28)

            # If the 14-day window for this year has already passed, 
            # the perk isn't "eligible" anyway, but for the countdown 
            # we target the end of the current window:
            expiry_date = this_year_bday + timedelta(days=14)

            # Convert date to aware datetime for the countdown
            return timezone.make_aware(timezone.datetime.combine(expiry_date, timezone.datetime.max.time()))
    
        return self.perk.valid_to


class CustomerVoucher(models.Model):
    id                          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value                       = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    balance                     = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    owner                       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="vouchers")
    purchaser_email             = models.EmailField()
    registered_email            = models.EmailField(null=True, blank=True)
    is_claimed                  = models.BooleanField(default=False)
    claimed_date                = models.DateTimeField(null=True, blank=True)
    is_used                     = models.BooleanField(default=False)
    used_date                   = models.DateTimeField(null=True, blank=True)
    created_date                = models.DateTimeField(auto_now_add=True)
    updated_date                = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.purchaser_email} - CNY {self.value}"
    
    def generate_registration_link(self, request):
        return request.build_absolute_uri(reverse('claim_voucher_url', args=[str(self.id)]))
    
    def claim(self, user_email):
        if not self.is_claimed:
            self.registered_email = user_email
            self.is_claimed = True
            self.claimed_date = timezone.now()
            self.save()
            return True
        return False


class ChatMessage(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.content}"

    def save(self, *args, **kwargs):
        """
        Custom save method to handle image resizing in memory 
        before saving to storage (Local or Cloud).
        """
        if len(self.content) > 1000:
            raise ValidationError("Content cannot exceed 255 characters.")
        if self.image:
            # 1. Open the image directly from the field
            img = Image.open(self.image)
            # Check if resizing is needed
            if img.height > 800 or img.width > 800:
                # 2. Resize
                img.thumbnail((800, 800))
                # 3. Prepare the buffer (RAM)
                buffer = io.BytesIO()
                # Get original format (JPEG, PNG, etc.) to maintain consistency
                img_format = img.format if img.format else 'JPEG'
                img.save(buffer, format=img_format, quality=85)
                # 4. Point the field to the new resized data
                # Use save=False here to prevent the model from saving itself again
                # and creating an infinite loop.
                filename = self.image.name
                self.image.save(filename, ContentFile(buffer.getvalue()), save=False)
        # 5. Call the 'real' save method to write to the database
        super().save(*args, **kwargs)