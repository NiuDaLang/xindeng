from .models import UserPerk
from datetime import timedelta, date
from django.utils import timezone


class PerkEvaluator:
    @staticmethod
    def get_eligibility_status(user, perk):
        # 0. Global Usage Check
        if not perk.has_available_uses():
            print("perk does NOT have available uses: ", perk.has_available_uses())
            return "OUT_OF_STOCK"
        
        # 1. Basic Perk Validity (Date/Usage)
        if not perk.is_active or not perk.is_within_validity_period():
            return "EXPIRED"
        
        # 🌟 GUEST INTERCEPT GATEKEEPER
        # If the shopper is an anonymous guest user, bypass all user-profile database dependencies!
        if not user or not user.is_authenticated:
            # Prevent guests from using highly exclusive account-bound tokens
            code_upper = perk.code.upper()
            if any(token in code_upper for token in ["NEW_MEMBER", "BIRTHDAY", "FEMALE_ONLY"]):
                return "MEMBER_ONLY_PERK"
                
            print(f"Guest session verified. Coupon code [{perk.code}] passed global eligibility benchmarks.")
            return "VALID"
        
        # -----------------------------------------------------------------
        # 🔒 MEMBER-ONLY LIFECYCLE TRACKERS (Only runs if user.is_authenticated)
        # -----------------------------------------------------------------
        # 2. Check if already used
        if UserPerk.objects.filter(user=user, perk=perk, is_used=True).exists():
            return "ALREADY_USED"

        # 3. Type-Specific Logic
        code = perk.code.upper()
        
        # (1) New Member Discount (First 30 days)
        if "NEW_MEMBER" in code:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            print("new member? ",  user.date_joined >= thirty_days_ago)
            if not user.date_joined >= thirty_days_ago:
                print("date joined > 30 days")
                return "NEW_MEMBER_PERK_EXPIRED"

        # (2) Birthday Discount (14-day window)
        if "BIRTHDAY" in code:
            if not hasattr(user, 'profile') or not user.profile.dob: 
                return "NO_DOB_DATA"
            today = date.today()
            bday = user.profile.dob.replace(year=today.year)
            # Window: Bday to Bday + 14 days
            print("Bday period? ", bday <= today <= (bday + timedelta(days=14)))
            if not bday <= today <= (bday + timedelta(days=14)):
                print("bday and today > 14 days")
                return "THIS_BIRTHDAY_PERK_EXPIRED"

        # (3) Gender-Specific
        if "FEMALE_ONLY" in code:
            # First check if the profile even exists
            if not hasattr(user, 'profile'):
                return "NO_PROFILE_DATA"
            
            # Now it is safe to check the gender
            if user.profile.gender != 'FEMALE':
                return "FEMALE_ONLY"

        return "VALID"

# class PerkEvaluator:
#     @staticmethod
