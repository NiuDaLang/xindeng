from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, UserProductList, Perk, CustomerVoucher, Address, Perk, UserPerk, ChatMessage
from django.utils.html import format_html
from .evaluators import PerkEvaluator


# get user model
from django.contrib.auth import get_user_model
Account = get_user_model()

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active', 'receive_newsletter')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%; object-fit: cover;">', object.profile_picture.url)
        return "No Image"
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'gender', 'color')


class UserProductListAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_variation', 'list_type', 'added_date')


class CustomerVoucherAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'balance', 'owner', 'purchaser_email', 'registered_email', 'is_claimed', 'claimed_date', 'is_used', 'used_date', 'created_date', 'updated_date')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('profile', 'is_default', 'label', 'address_line_1', 'address_line_2', 'city', 'state_province_region', 'postal_code', 'country', 'is_verified_by_google', 'last_updated')


class PerkAdmin(admin.ModelAdmin):
    # 🌟 converted from tuples to list matrices for scalability
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_to', 'uses_count']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
    
    # 🌟 FIXED: Removed 'uses_count' from here so it becomes fully editable!
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ['General Info', {'fields': ['code', 'description', 'featured_image', 'is_active']}],
        ['Discount Settings', {'fields': ['discount_type', 'discount_value', 'min_spending_requirement']}],
        ['Usage & Validity', {'fields': ['valid_from', 'valid_to', 'max_uses', 'uses_count']}],
        ['Timestamps', {'fields': ['created_at', 'updated_at']}],
    ]

    def save_model(self, request, obj, form, change):
        """
        Cleans any latent database F() expressions before saving the form data,
        ensuring that manual edits to uses_count always overwrite code tracking fields safely.
        """
        if hasattr(obj.uses_count, 'resolve_expression'):
            obj.uses_count = form.cleaned_data.get('uses_count', 0)
        super().save_model(request, obj, form, change)
        

class UserPerkAdmin(admin.ModelAdmin):
    list_display = ('unique_code', 'user', 'perk', 'is_used', 'used_at', 'check_eligibility')
    list_filter = ('is_used', 'perk')
    search_fields = ('unique_code', 'user__username', 'user__email', 'perk__code')
    readonly_fields = ('unique_code', 'used_at')
    raw_id_fields = ('user', 'perk') # Better for performance if you have many users

    def check_eligibility(self, obj):
        """
        Uses your PerkEvaluator to show real-time eligibility in the list view.
        """
        is_eligible = PerkEvaluator.get_eligibility_status(obj.user, obj.perk)
        if is_eligible == "VALID":
            return "✅ Eligible"
        return "❌ Ineligible / Expired"
    
    check_eligibility.short_description = 'Evaluator Status'


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'content', 'image', 'timestamp', 'is_read')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserProductList, UserProductListAdmin)
admin.site.register(Perk, PerkAdmin)
admin.site.register(CustomerVoucher, CustomerVoucherAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserPerk, UserPerkAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
