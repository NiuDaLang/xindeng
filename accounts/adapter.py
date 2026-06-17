from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile
import requests
from django.core.files.base import ContentFile

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

            # 🌟 THE NET FIX: Dynamically download and store the avatar image file locally
            google_avatar_url = extra_data.get('picture')
 
            # 🌟 ACCURATE FILEHANDSHAKE CHECK:
            # If Google passes a valid image URL link, download it onto local disk storage
            if google_avatar_url and not profile.profile_picture:
                # Catch if Google passes a dummy string parameter or internal documentation placeholder
                if "daisyui" not in google_avatar_url:
                    try:
                        response = requests.get(google_avatar_url, timeout=5)
                        if response.status_code == 200:
                            file_name = f"user_{user.id}_google_avatar.jpg"
                            profile.profile_picture.save(
                                file_name, 
                                ContentFile(response.content), 
                                save=False
                            )
                            print(f"📸 Cached Google Account Avatar locally for User {user.id}")
                    except Exception as e:
                        print(f"⚠️ Image download skipped due to connection timeout: {str(e)}")
            
            # If no image was downloaded, map the default fallback path to keep things clean
            if not profile.profile_picture:
                profile.profile_picture = "userprofile/default.png"
                
            profile.save()
        
        return user