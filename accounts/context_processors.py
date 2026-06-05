from django.conf import settings


def get_google_api(request):
    return {
        "GOOGLE_API_KEY": getattr(settings, "GOOGLE_API_KEY", None)
    }