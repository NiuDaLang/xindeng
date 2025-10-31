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

    return render(request, "accounts/dashboard_main.html", context)


def member_profile(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "會員資料",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/member_profile",
    }

    return render(request, "accounts/dashboard_profile.html", context)


def addresses(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "地址",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/addresses",
    }

    return render(request, "accounts/dashboard_addresses.html", context)


def orders(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "訂單紀錄",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/orders",
    }
    return render(request, "accounts/dashboard_orders.html", context)


def order(request):
    user = request.user
    order_num = 'xxxxxxx'
    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "訂單紀錄",
        "bread_crumb_4": f"訂單No.{order_num}",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/orders",
        "bread_crumb_4_url": "/accounts/dashboard/orders/order",
    }
    return render(request, "accounts/dashboard_order.html", context)


def help(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "幫助",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/help",
    }

    return render(request, "accounts/dashboard_help.html", context)


def wishlist(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "未來購物清單",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/wishlist",
    }

    return render(request, "accounts/dashboard_wishlist.html", context)


def favorites(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "收藏",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/favorites",
    }

    return render(request, "accounts/dashboard_favorites.html", context)


def coupons(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "優惠券",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/coupons",
    }

    return render(request, "accounts/dashboard_coupons.html", context)


def vouchers(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "禮品券",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/vouchers",
    }

    return render(request, "accounts/dashboard_vouchers.html", context)


def threed(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title": "XXXXX XXXXX",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "會員",
        "bread_crumb_3": "3D場景",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/threed",
    }

    return render(request, "accounts/dashboard_threed.html", context)


def firework(request):

    return render(request, "accounts/three/firework.html")