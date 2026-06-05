from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # 1 Save the basic user first
        user = super().save_user(request, sociallogin, form)

        extra_data = sociallogin.account.extra_data

        # 3. Custom Logic: Example of saving extra data to this User model
        if sociallogin.account.provider == 'google':
            user.is_active = True
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
            user.save()
            # Access UserProfile via related_name='profile' (from models.py)
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Google 'picture' is a URL string, but profile_picture is an ImageField.
            # Usually, store the URL in a separate URLField or download the image
            # For now just ensure the profile exists.
            profile.save()
        
        return user