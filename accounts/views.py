from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
def login(request):
    return render(request, "pages/login.html")


def register(request):
    return render(request, "pages/register.html")


def forgot_password(request):
    return render(request, "pages/forgot_password.html")


def reset_password(request):
    return render(request, "pages/reset_password.html")


def dashboard(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "",
    }

    return render(request, "pages/dashboard.html", context)