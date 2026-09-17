from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import RegistrationForm, ResetPasswordForm, UserForm, UserProfileForm, AddressForm, AddressBookForm
import json
from django.contrib import auth
from django.views.decorators.debug import sensitive_post_parameters
from.models import CustomerVoucher, ChatMessage
from store.models import ProductVariation
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from carts.views import _cart_id
from django.db import transaction
from django.db.models import Q, Count
from django.utils.safestring import mark_safe
import re
from django.http import Http404
from django.contrib.auth import login as auth_login
from orders.tasks import send_secure_voucher_pin_email_task
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from accounts.templatetags.chat_extras import format_chat

import uuid
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.urls import reverse
from carts.utils import update_header_cart_summary, get_total_wallet_funds, get_cash_voucher_balance, get_cash_voucher_pending_holds_total

# get user model
from django.contrib.auth import get_user_model
Account = get_user_model()
from .models import UserProfile, UserProductList, Address, Perk, UserPerk
from .evaluators import PerkEvaluator

# verification email
from django.contrib.sites.shortcuts import get_current_site
from emails.utils import send_account_verification, send_password_reset, send_password_reset_completion
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

import datetime
from .utils import get_current_solar_term_period, check_today_is_solar_term, get_next_solar_term, htmx_unavailable_response
import opencc
from .data import SOLAR, DESTINATIONS_MAINLAND_CHINA
from deep_translator import GoogleTranslator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.timesince import timesince

import random
from django.db.models import Sum
from decimal import Decimal
from orders.models import OrderVoucherUsage
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

NUM_MSG_PER_LOAD = 10


# Create your views here.
@sensitive_post_parameters("password", "password1", "password2")
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            receive_newsletter = form.cleaned_data["receive_newsletter"]
            password = form.cleaned_data["password1"]

            user = Account.objects.create_user(
                username=username,
                email=email,
                receive_newsletter=receive_newsletter,
                password=password, # Pass it here!
            )

            # 🌟 DEDICATED SEPARATE INTERCEPT: Cache guest cancellations under its own key
            # This keeps your pre-existing 'pending_claim_voucher_id' for gifted cards completely safe!
            claim_voucher_id = request.GET.get('claim_voucher_id')
            if claim_voucher_id:
                request.session['pending_cancellation_voucher_id'] = claim_voucher_id
                request.session.modified = True
                print(f"💾 CANCELLATION CACHE SUCCESS: Logged guest refund voucher {claim_voucher_id} inside user session channel.")

            # user activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your Hṛdayadīpa (हृदयदीप) account｜請激活您的【心燈】帳號"

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            to_email = user.email

            send_account_verification(mail_subject, user, [to_email], current_site, uid, token)

            # messages.success(request, "感謝註冊！我們已向您的信箱發送了一封驗證郵件。 | Thank you for registering with us. We have sent you an verification email to your email address.")

            form_errors = None
            email_errors = None
            username_errors = None
            pw_errors = None
            return redirect('/accounts/login/?command=verification&email='+email)

        elif form.errors:
            form_errors = json.loads(form.errors.as_json())
            # email error
            if "email" in form_errors:
                email_errors = form_errors["email"]
                for error in email_errors:
                    if error['code'] == "unique":
                        error['message'] = "此電子郵件已被註冊 | Email already exists."
                    elif error['code'] == "invalid":
                        error['message'] = "請輸入有效的電子郵件 | Invalid email address."
            else:
                email_errors = None
            # username error
            if "username" in form_errors:
                username_errors = form_errors["username"]
                for error in username_errors:
                    if error['code'] == "unique":
                        error['message'] = "此用戶名已被註冊 | Username already exists."
                    elif error['code'] == "invalid":
                        error['message'] = "請輸入有效的用戶名 | Invalid username."
            else:
                username_errors = None
            # password error
            if "password2" in form_errors:
                pw_errors = form_errors["password2"]
                for error in pw_errors:
                    if(error['code'] == "password_mismatch"):
                        error['message'] = "密碼與確認密碼不相符 | Passwords do not match."
                    elif(error['code'] == "password_too_short"):
                        num_char = error['message'].split("This password is too short. It must contain at least ")[1].split(" characters.")[0]
                        error['message'] = f"密碼太短，至少{num_char}個字 | Password is too short. At least {num_char} characters."
                    elif(error['code'] == "password_too_common"):
                        error['message'] = "密碼太簡單，請選擇更安全的密碼 | Password is too common."
                    elif(error['code'] == "password_entirely_numeric"):
                        error['message'] = "密碼不能為純數字 | Password cannot be entirely numeric."
                    elif(error['code'] == "password_user_attribute_similar_to_email"):
                        error['message'] = "密碼不能為電子郵件 | Password cannot be similar to email."
                    elif(error['code'] == "password_too_similar"):
                        error['message'] = "密碼太像電子郵件 | Password is too similar to email."
                    elif(error['code'] == "password_too_similar_to_username"):
                        error['message'] = "密碼太像用戶名 | Password is too similar to username."
                    elif(error['code'] == "password_too_similar_to_first_name"):
                        error['message'] = "密碼太像名字 | Password is too similar to first name."
                    elif(error['code'] == "password_too_similar_to_last_name"):
                        error['message'] = "密碼太像姓氏 | Password is too similar to last name."
                    elif(error['code'] == "password_too_similar_to_other_field"):
                        error['message'] = "密碼太像其他欄位 | Password is too similar to other field."
                    elif(error['code'] == "min_length_special_characters"):
                        error['message'] = "密碼至少要有一個特殊字元 | Password must contain at least one special character."
                    elif(error['code'] == "min_length_numeric_characters"):
                        error['message'] = "密碼至少要有一個數字 | Password must contain at least one numeric character."
                    elif(error['code'] == "min_length_uppercase_characters" or error['code'] == "min_length_upper_characters"):
                        error['message'] = "密碼至少要有一個大寫字母 | Password must contain at least one uppercase character."
                    elif(error['code'] == "min_length_lowercase_characters" or error['code'] == "min_length_lower_characters"):
                        error['message'] = "密碼至少要有一個小寫字母 | Password must contain at least one lowercase character."
                    elif(error['code'] == "min_length_alpha"):
                        error['message'] = "密碼至少要有一個字母 | Password must contain at least one letter."
                    elif(error['code'] == "password_used"):
                        error['message'] = "密碼已經被使用過 | Password has been used before."
            else:
                pw_errors = None

    else:
        form = RegistrationForm()
        form_errors = None
        pw_errors = None
        email_errors = None
        username_errors = None

    context = {
        "google_client_id": os.environ.get('GOOGLE_CLIENT_ID'),
        "form": form,
        "form_errors": form_errors,
        "email_errors": email_errors,
        "pw_errors": pw_errors,
        "username_errors": username_errors,
        "page_title": "Register｜註冊"
    }
    return render(request, "pages/register.html", context)


def activate(request, uidb64, token):       
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # 🌟 THE NET FIX: Auto-authenticate and log in the user on verification success
        auth_login(request, user)

        success_messages_list = ["帳號已成功激活！ | Account activated!"]

        # 🎁 WORKFLOW 1: Pre-existing Gifted Cash Voucher Logic Loops (Left completely untouched)
        pending_voucher_id = request.session.pop('pending_claim_voucher_id', None)
        if pending_voucher_id:
            try:
                voucher = CustomerVoucher.objects.get(id=pending_voucher_id, is_claimed=False)
                voucher.owner = user
                voucher.claim(user.email)
                messages.success(request, f"帳號已成功激活！且面值 CNY {voucher.value} 的禮品券已自動匯入您的錢包。 | Account activated! Voucher worth CNY {voucher.value} has been added to your wallet.")
            except CustomerVoucher.DoesNotExist:
                messages.success(request, "Account activated｜帳號已成功激活")
        else:
            messages.success(request, "Account activated｜帳號已成功激活")

        # 🎁 WORKFLOW 1: Pre-existing Gifted Cash Voucher Logic Loops (Left completely untouched)
        pending_gift_voucher_id = request.session.pop('pending_claim_voucher_id', None)
        if pending_gift_voucher_id:
            try:
                gift_voucher = CustomerVoucher.objects.get(id=pending_gift_voucher_id, is_claimed=False)
                gift_voucher.owner = user
                gift_voucher.claim(user.email)
                success_messages_list.append(f"面值 CNY {gift_voucher.value} 的贈送禮品券已自動匯入您的錢包。 | Gifted voucher worth CNY {gift_voucher.value} has been added to your wallet.")
            except (CustomerVoucher.DoesNotExist, ValueError):
                pass

        # 🎫 WORKFLOW 2: The New Automated Guest Cancellation Refund Engine
        pending_cancel_voucher_id = request.session.pop('pending_cancellation_voucher_id', None)
        if pending_cancel_voucher_id:
            try:
                cancel_voucher = CustomerVoucher.objects.get(id=pending_cancel_voucher_id, is_claimed=False)
                
                # Verify that the voucher has not passed its 1-year legal lifespan
                if cancel_voucher.is_expired():
                    messages.warning(request, "該取消訂單退回之全額購物金已超過一年領取時限，面值已自動失效。 | However, your order cancellation credit has expired (1-year claim window exceeded).")
                else:
                    cancel_voucher.owner = user
                    cancel_voucher.claim(user.email)
                    success_messages_list.append(f"因取消訂單退回面值 CNY {cancel_voucher.value} 的全額購物金已成功存入。 | Cancellation refund voucher worth CNY {cancel_voucher.value} has been added to your account.")
                    print(f"🎉 GUEST REFUND VOUCHER REDEEMED: Token {cancel_voucher.id} successfully claimed by {user.email}")
            except (CustomerVoucher.DoesNotExist, ValueError):
                pass

        # Display the aggregated success array blocks clearly on their screen viewport
        messages.success(request, " ".join(success_messages_list))
            
        # Redirect directly into their dashboard panel since they are now fully logged in
        return redirect("dashboard", subpage="main")
    else:
        messages.error(request, "Invalid activation link or token expired. ｜激活連結無效或驗證權杖已過期")
        return redirect("register")
    

def login(request, user=None):
    if request.user.is_authenticated:
        return redirect("dashboard", subpage="main")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 🌟 CRITICAL FIX: Capture the immutable guest session key string BEFORE auth.login flushes the container
        # We check both your custom middleware attribute fallback and the raw session token parameter
        anonymous_guest_key = getattr(request, 'prior_session_key', None) or request.session.session_key
        saved_next_url = request.session.get("next_url")
        print("anonymous_guest_key: ", anonymous_guest_key)
        print("saved_next_url: ", saved_next_url)
        user = auth.authenticate(request, username=email, password=password)

        if user is not None:
            # Django securely cycles the session token keys right here
            auth.login(request, user)

            # 🔒 SANITATION ACTION: Clear applied pricing codes during login transitions
            # This prevents guest code values from carrying over into authenticated user states
            if "offer_applied" in request.session:
                request.session.pop("offer_applied", None)
                request.session.modified = True
            if saved_next_url:
                request.session["next_url"] = saved_next_url
                request.session.modified = True
            
            # 🌟 SURGICAL DATA MERGE ENGINE: Migrate anonymous records using the captured key
            if anonymous_guest_key:
                print(f"Migrating guest cart data from session key: {anonymous_guest_key} to user: {user.email}")
                
                guest_cart = Cart.objects.filter(cart_id=anonymous_guest_key, user__isnull=True).first()
                if guest_cart:
                    # Retrieve or initialize the permanent logged-in user cart record mapping
                    member_cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': anonymous_guest_key})
                    guest_items = CartItem.objects.filter(cart=guest_cart, is_active=True)
                    
                    for item in guest_items:
                        # Cross-reference if this product variation already exists inside the member's cart
                        existing_member_item = CartItem.objects.filter(cart=member_cart, product_variation=item.product_variation).first()
                        
                        if existing_member_item:
                            existing_member_item.quantity += item.quantity
                            existing_member_item.save()
                            item.delete() # Drop duplicate guest entries safely
                        else:
                            item.cart = member_cart
                            if hasattr(item, 'user'):
                                item.user = user
                            item.save()
                            
                        # 🌟 WISHLIST CLEANUP ENGAGEMENT: Drop item from user's wishlist if it's now in their cart
                        UserProductList.objects.filter(
                            user=user, 
                            product_variation=item.product_variation, 
                            list_type='WISHLIST'
                        ).delete()
                    
                    # Clean up the old, empty guest cart container from the database
                    guest_cart.delete()

            # Voucher validation hooks
            pending_voucher_id = request.session.pop('pending_claim_voucher_id', None)
            if pending_voucher_id:
                try:
                    voucher = CustomerVoucher.objects.get(id=pending_voucher_id, is_claimed=False)
                    voucher.owner = user
                    voucher.claim(user.email)
                    messages.success(request, f"Welcome back! A CNY {voucher.value} gift voucher has been automatically added to your wallet.｜歡迎回來！面值 CNY {voucher.value} 的禮品券已自動匯入您的錢包。")
                except CustomerVoucher.DoesNotExist:
                    pass
            else:
                messages.success(request, "Login successful｜登入成功")

            next_url = request.session.pop("next_url", None)
            if next_url:
                print(f"🔄 REDIRECTING INTERCEPTED USER: Routing straight back to payment flow target: {next_url}")

             # Check if this login form submission was generated via an HTMX AJAX call
                if request.headers.get("HX-Request"):
                    response = HttpResponse("", status=200)
                    response["HX-Redirect"] = next_url
                    return response
                    
                return redirect(next_url)               
        
            return redirect("dashboard", subpage="main")
        else:
            messages.error(request, "Login failed｜登入失敗")
            return redirect("login")
    
    return render(request, "pages/login.html", {"page_title": "Login｜登入"})


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful｜登出成功")
    return redirect("login")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # reset password email
            current_site = get_current_site(request)
            mail_subject = "Please reset your Hṛdayadīpa (हृदयदीप) password | 請重設您的【心燈】密碼"

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            to_email = user.email

            send_password_reset(mail_subject, user, [to_email], current_site, uid, token)

            # messages.info(request, "我們已向您的信箱發送了一封重設密碼郵件。 | We have sent you an email to reset your password.")
            return redirect('/accounts/login/?command=reset_password&email='+email)
        else:
            messages.error(request, "This account does not exist｜此帳號不存在")
            return redirect("forgot_password")

    return render(request, "pages/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password｜請重設您的密碼")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has expired｜重設密碼連結已無效")
        return redirect("login")


def reset_password(request):
    try:
        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)
    except:
        user = None

    if user is None:
        return redirect('login')
    
    elif user is not None:
        if request.method == "POST":
            form = ResetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, user) # if logged in, no need to be logged off
                # send notification
                mail_subject = "您已完成密碼重設 | Password Reset Confirmation"
                to_email = user.email
                current_site = get_current_site(request)

                send_password_reset_completion(mail_subject, user, [to_email], current_site)
                messages.success(request, "Password has been reset｜密碼已重設")
                return redirect("login")
            elif form.errors:
                form_errors = json.loads(form.errors.as_json())
                if "new_password2" in form_errors:
                    pw_errors = form_errors["new_password2"]
                    for error in pw_errors:
                        if(error['code'] == "password_mismatch"):
                            # error['message'] = "密碼與確認密碼不相符 | Passwords do not match."
                            messages.error(request, "Passwords do not match｜兩次密碼輸入不一致")
                        elif(error['code'] == "password_too_short"):
                            num_char = error['message'].split("This password is too short. It must contain at least ")[1].split(" characters.")[0]
                            # error['message'] = f"密碼太短，至少{num_char}個字 | Password is too short. At least {num_char} characters."
                            messages.error(request, f"Password is too short. At least {num_char} characters｜密碼太短，至少{num_char}個字")
                        elif(error['code'] == "password_too_common"):
                            # error['message'] = "密碼太簡單，請選擇更安全的密碼 | Password is too common."
                            messages.error(request, "Password is too common｜密碼太簡單，請選擇更安全的密碼")
                        elif(error['code'] == "password_entirely_numeric"):
                            # error['message'] = "密碼不能為純數字 | Password cannot be entirely numeric."
                            messages.error(request, "Password cannot be entirely numeric｜密碼不能為純數字")
                        elif(error['code'] == "password_user_attribute_similar_to_email"):
                            # error['message'] = "密碼不能為電子郵件 | Password cannot be similar to email."
                            messages.error(request, "Password cannot be similar to email｜密碼不能為電子郵件")
                        elif(error['code'] == "password_too_similar"):
                            # error['message'] = "密碼太像電子郵件 | Password is too similar to email."
                            messages.error(request, "Password is too similar to email｜密碼太像電子郵件")
                        elif(error['code'] == "password_too_similar_to_username"):
                            # error['message'] = "密碼太像用戶名 | Password is too similar to username."
                            messages.error(request, "Password is too similar to username｜密碼太像用戶名")
                        elif(error['code'] == "password_too_similar_to_first_name"):
                            # error['message'] = "密碼太像名字 | Password is too similar to first name."
                            messages.error(request, "Password is too similar to first name｜密碼太像名字")
                        elif(error['code'] == "password_too_similar_to_last_name"):
                            # error['message'] = "密碼太像姓氏 | Password is too similar to last name."
                            messages.error(request, "Password is too similar to last name｜密碼太像姓氏")
                        elif(error['code'] == "password_too_similar_to_other_field"):
                            # error['message'] = "密碼太像其他欄位 | Password is too similar to other field."
                            messages.error(request, "Password is too similar to other field｜密碼太像其他欄位")
                        elif(error['code'] == "min_length_special_characters"):
                            # error['message'] = "密碼至少要有一個特殊字元 | Password must contain at least one special character."
                            messages.error(request, "Password must contain at least one special character｜密碼至少要有一個特殊字元")
                        elif(error['code'] == "min_length_numeric_characters"):
                            # error['message'] = "密碼至少要有一個數字 | Password must contain at least one numeric character."
                            messages.error(request, "Password must contain at least one numeric character｜密碼至少要有一個數字")
                        elif(error['code'] == "min_length_uppercase_characters" or error['code'] == "min_length_upper_characters"):
                            # error['message'] = "密碼至少要有一個大寫字母 | Password must contain at least one uppercase character."
                            messages.error(request, "Password must contain at least one uppercase character｜密碼至少要有一個大寫字母")
                        elif(error['code'] == "min_length_lowercase_characters" or error['code'] == "min_length_lower_characters"):
                            # error['message'] = "密碼至少要有一個小寫字母 | Password must contain at least one lowercase character."
                            messages.error(request, "Password must contain at least one lowercase character｜密碼至少要有一個小寫字母")
                        elif(error['code'] == "min_length_alpha"):
                            # error['message'] = "密碼至少要有一個字母 | Password must contain at least one letter."
                            messages.error(request, "Password must contain at least one letter｜密碼至少要有一個字母")
                        elif(error['code'] == "password_used"):
                            # error['message'] = "密碼已經被使用過 | Password has been used before."
                            messages.error(request, "Password has been used before｜密碼已經被使用過")
            context = { "form": form }
        else:
            form = ResetPasswordForm(user)
            context = { "form": form }

    return render(request, "pages/reset_password.html", context)


def check_username(request):
    username = request.GET.get('username', '').strip()
    
    # 1. Don't trigger error if it's the user's current name or empty
    if not username or username == request.user.username:
        return HttpResponse("")

    # 2. Check if exists in DB
    if Account.objects.filter(username__iexact=username).exists():
        return HttpResponse(
            '<span class="text-error text-xs">❌ This username is taken | 此用戶名已被使用</span>'
        )
    
    # 3. Optional: Show success message
    return HttpResponse('<span class="text-success text-xs">✅ Available | 可以使用</span>')


@login_required(login_url='login')
def dashboard(request, subpage):
    if not request.user.is_authenticated:
        print("not logged in!")
        return redirect('login')
  
    # main
    templates = {
        'main': 'accounts/dashboard_main.html',
        'profile': 'accounts/dashboard_profile.html',
        'addresses': 'accounts/dashboard_addresses.html',
        'orders': 'accounts/dashboard_orders.html',
        'offers': 'accounts/dashboard_offers.html',
        'vouchers': 'accounts/dashboard_vouchers.html',
        'wishlist': 'accounts/dashboard_wishlist.html',
        'favorites': 'accounts/dashboard_favorites.html',
        'help': 'accounts/dashboard_help.html',
        'threed': 'accounts/dashboard_threed.html',
    }
    page_title = {
        'main': 'Main｜管理主頁',
        'profile': 'Edit Profile｜會員檔案',
        'addresses': 'Addresses｜地址簿',
        'orders': 'Orders｜購物紀錄',
        'offers': 'Offers｜福利活動',
        'vouchers': 'Vouchers｜禮品券',
        'wishlist': 'Wishlist｜購物清單',
        'favorites': 'Favorites｜收藏',
        'help': 'Help｜客服熱線',
        'threed': '3D Scenes｜三維場景',
    }
    template_name = templates.get(subpage, 'accounts/dashboard_main.html')
    subpage_title = page_title.get(subpage, 'Main｜管理主頁')
    chat_messages = ChatMessage.objects.none()
    member_id = request.session.get('chat_member_id')
    context = {}

    ### general ###
    # 節氣
    today = datetime.date.today()
    today_is_solar_term = check_today_is_solar_term(today)
    current_term, start_date = get_current_solar_term_period(today)
    trad_term, term_en, trad_next_term = None, None, None
    next_term, next_term_en = None, None
    translator = opencc.OpenCC('s2t.json')

    # 🎨 24 SOLAR TERM BACKING IMAGES TRACK INDEX (Using Simplified Chinese Keys)
    solar_term_imgs = {
        "小寒": "minor_cold.webp",
        "大寒": "major_cold.webp",
        "立春": "beginning_of_spring.webp",
        "雨水": "rain_water.webp",
        "惊蛰": "awakening_of_text.webp",
        "春分": "spring_equinox.webp",
        "清明": "pure_brightness.webp",
        "谷雨": "grain_rain.webp",
        "立夏": "beginning_of_summer.webp",
        "小满": "grain_buds.webp",
        "芒种": "grain_in_ear.webp",
        "夏至": "summer_solstice.webp",
        "小暑": "minor_heat.webp",
        "大暑": "major_heat.webp",
        "立秋": "beginning_of_autumn.webp",
        "处暑": "end_of_heat.webp",
        "白露": "white_dew.webp",
        "秋分": "autumnal_equinox.webp",
        "寒露": "cold_dew.webp",
        "霜降": "frost_descent.webp",
        "立冬": "beginning_of_winter.webp",
        "小雪": "minor_snow.webp",
        "大雪": "major_snow.webp",
        "冬至": "winter_solstice.webp",
    }

    # 🔒 ROBUST FAILSAFE EVALUATION ROUTER
    current_term_img = "hero/red_leaves.jpeg"  # Fallback to default asset if lookups omit keys

    if current_term:
        trad_term = translator.convert(current_term)
        term_en = SOLAR[current_term]
        
        # Extract the matching image file name. Adjust folders string safely to match media directories
        if current_term in solar_term_imgs:
            current_term_img = f"solar_terms/{solar_term_imgs[current_term]}"
            
    if not today_is_solar_term:
        next_term = get_next_solar_term(current_term)
        trad_next_term = translator.convert(next_term[0])
        next_term_en = next_term[1]

    context.update({
        # general
        "subpage_template": template_name,
        "subpage": subpage,
        "user": request.user,
        "solar_term": trad_term,
        "solar_term_en": term_en,
        "next_solar_term": trad_next_term,
        "next_solar_term_en": next_term_en,
        "solar_term_bg_url": f"{settings.MEDIA_URL}{current_term_img}",
    })

    # main
    # 1. Calculate historical purchased quantities cleanly inside database indexes
    total_items_purchased = OrderProduct.objects.filter(
        order__user=request.user,
        product__is_voucher=False,
        order__order_status='Delivered'
    ).aggregate(t_qty=Sum('quantity'))['t_qty'] or 0

    # 2. Wallet balance
    wallet_balance = get_total_wallet_funds(request)
    free_cash = get_cash_voucher_balance(request)
    pending_holds_total = get_cash_voucher_pending_holds_total(request)

    # 3. Pull dynamic unread communications counts
    unread_count = 0 # Re-link to your customer messaging channels loops later

    # 🌟 4. ACTIVE TRACKER PIPELINE QUERY: Fetch in-flight split fulfillments safely!
    in_progress_orders = Order.objects.filter(
        user=request.user,
        is_ordered=True,
        order_status__in=['Processing', 'Partly_Dispatched', 'All_Dispatched']
    ).order_by('-ordered_at')

    context.update({
        # main
        "total_items_purchased": total_items_purchased,
        "wallet_balance": wallet_balance,
        "free_cash": free_cash,
        "pending_holds_total": pending_holds_total,
        "unread_count": unread_count,
        "in_progress_orders": in_progress_orders,
    })

    # edit profile
    user_profile = None
    user_form = None
    profile_form = None
    address_form = None
    user_form_errors = None
    profile_form_errors = None
    address_form_errors = None
    if subpage == "profile":
        # 1. Get or create the profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        # 2. Get the existing default address (if any)
        default_address = Address.objects.filter(profile=user_profile, is_default=True).first()

        if request.method == "POST":
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            address_form = AddressForm(request.POST, instance=default_address)

            # Inside dashboard view -> POST -> after is_valid()
            if user_form.is_valid() and profile_form.is_valid() and address_form.is_valid():
                try:
                    with transaction.atomic():
                        user_form.save()
                        profile_form.save()

                        address_1 = address_form.cleaned_data.get('address_line_1')

                        if address_1 and address_1.strip():                        
                            # Process the address
                            address = address_form.save(commit=False)
                            if not address.address_line_1:
                                address.is_verified_by_google = False                            
                            if address_form.cleaned_data.get('country') == 'CN':
                                address.state_province_region = address_form.cleaned_data.get('china_province')
                            address.profile = user_profile  # Link to the user
                            address.is_default = True       # Force this to be the primary address
                            address.save()                  # This triggers your model's custom save() logic
                        else:
                            # Optional: If address is blank, delete the default address to clear it out
                            if default_address:
                                default_address.delete()
                        
                    messages.success(request, "Your profile has been updated｜您的個人資料已更新")
                    return redirect("dashboard", subpage="profile")
                except Exception as e:
                    # 1. Capture the original error message
                    original_error = str(e)
                    # 2. Translate it to Traditional Chinese (zh-TW)
                    translated_message = GoogleTranslator(source='en', target='zh-TW').translate(original_error)
                    messages.error(request, f"Error: {str(e)}|{translated_message}")
            else:
                # 1. Collect all errors from all forms into a list
                all_errors = []
                for form in [user_form, profile_form, address_form]:
                    for field, errors in form.errors.items():
                        field_name_en = field.replace('_', ' ').title()
                        error_en = errors.as_text()
                        field_name_cn = GoogleTranslator(source='en', target='zh-TW').translate(field_name_en)
                        error_cn = GoogleTranslator(source='en', target='zh-TW').translate(error_en)
                        all_errors.append(f"{field_name_en}: {error_en}｜{field_name_cn}: {error_cn}")
                
                # 2. Join them with a new line or bullet point
                error_message = "\n".join(all_errors)

                # 3. Add to messages with a specific extra_tag for SWAL
                messages.error(request, error_message)
        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=user_profile)
            address_form = AddressForm(instance=default_address)    

        context.update({
            # profile
            "user_profile": user_profile,
            "user_form": user_form,
            "profile_form": profile_form,
            "address_form": address_form,
            "user_form_errors": user_form_errors,
            "profile_form_errors": profile_form_errors,
            "address_form_errors": address_form_errors,
            # sub_title_2
            "sub_title_2": page_title.get(subpage, 'Main｜管理主頁')
        })            

    # addresses
    address_book_form = None
    user_addresses = None
    submit_btn = None
    address_exists = None
    if subpage == "addresses":
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_addresses = Address.objects.filter(profile=user_profile)
        address_book_form = AddressBookForm()
        submit_btn = "Create｜新&nbsp;增"
        context.update({
            "user_addresses": user_addresses,
            "address_book_form": address_book_form,
            "submit_btn": submit_btn,
            "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,
            "has_saved_addresses": user_addresses.exists(), 
        })   

    # orders
    visible_orders = None
    
    if subpage == "orders":
        # 1. Base query restricted to the authenticated user account
        order_query = Order.objects.filter(user=request.user)      

        # 2. Extract HTMX control and filter parameters
        sort_by = request.GET.get('sort', '-created_at')
        status_filter = request.GET.get('status', 'ALL')
        search_num = request.GET.get('search_invoice', '').strip()
        is_expanded = request.GET.get('expand', 'false') == 'true'

        # 3. Apply operational search filters across tracking tokens
        if search_num:
            order_query = order_query.filter(order_number__icontains=search_num)
            
        if status_filter != 'ALL':
            if status_filter == 'PENDING':
                # Fixed: Fallback directly to status checks or check against timezone updates safely
                order_query = order_query.filter(
                    is_ordered=False, 
                    order_status='Hold_Pending'
                )
            elif status_filter == 'PROCESSING':
                # Fixed: Implemented explicit OR constraints matching your summary metrics engine counters
                order_query = order_query.filter(
                    Q(order_status='Processing') | Q(is_ordered=True, order_status='Processing')
                )
            elif status_filter == 'COMPLETED':
                order_query = order_query.filter(order_status__in=['Delivered', 'All_Dispatched'])
            elif status_filter == 'CANCELLED':
                order_query = order_query.filter(order_status='Cancelled')

        print("order_query: ", order_query)

        # 4. Process dynamic ordering structures
        if sort_by in ['-created_at', 'created_at', 'order_number', '-order_number']:
            order_query = order_query.order_by(sort_by)
        else:
            order_query = order_query.order_by('-created_at')

        # 5. Cache global metrics flags for the dashboard stats indicators
        all_user_orders = Order.objects.filter(user=request.user)

        # 1. Total Paid Collection (Used for ledger history views)
        paid_orders = all_user_orders.filter(is_ordered=True).exclude(order_status='Cancelled')

        # 2. FIXED METRIC: Query status directly from the absolute base queryset
        # This ensures it captures orders cleanly regardless of row-locking commits
        in_process_paid_orders_count = all_user_orders.filter(
            Q(order_status='Processing') | Q(is_ordered=True, order_status='Processing')
        ).count()

        # 3. Completed Fulfillments count
        completed_orders_count = all_user_orders.filter(order_status__in=['Delivered', 'All_Dispatched']).count()

        # 4. Active pending bank wire holds within their expiration limit
        pending_orders_count = all_user_orders.filter(
            is_ordered=False, 
            order_status='Hold_Pending', 
            inventory_hold_expiry__gt=timezone.now()
        ).count()

        # 5. Apply pagination slicing layout metrics (Collapse to 4 records initially)
        total_found_count = order_query.count()
        print("total_found_count: ", total_found_count)
        total_found_count_oob = f'''
            <span id="total_found_count" hx-swap-oob="true" 
                    class="font-mono text-xs text-info-content font-black">
                    { total_found_count }
            </span>
        '''
        if not is_expanded and total_found_count > 4:
            visible_orders = order_query[:4]
            show_expand_btn = True
        else:
            visible_orders = order_query
            show_expand_btn = False

        # 6. Update layout context state arrays
        context.update({
            "all_user_orders": visible_orders,
            "total_found_count": total_found_count,
            "show_expand_btn": show_expand_btn,
            "current_sort": sort_by,
            "current_status": status_filter,
            "search_invoice": search_num,
            "is_expanded": is_expanded,
            "in_process_paid_orders_count": in_process_paid_orders_count,
            "completed_orders_count": completed_orders_count,
            "pending_orders_count": pending_orders_count,
        })

        # 7. HTMX Partial Swap Intercept for real-time list filtering
        if request.headers.get('HX-Request') and request.headers.get('HX-Target') == "orders_ledger_container":
            main_html = render_to_string("accounts/partials/orders_ledger_list.html", context, request=request)
            response = HttpResponse(main_html + total_found_count_oob)
            return response
              
    # offers
    eligible_perks = None
    if subpage == "offers":
        all_active_perks = Perk.objects.filter(is_active=True)
        eligible_perks = []
        print("all_active_perks")
        for perk in all_active_perks:
            status = PerkEvaluator.get_eligibility_status(request.user, perk)
            print("perk: status - ", perk, ": ", status)
            if status == 'VALID':
                # Using get_or_create is smart; it ensures the unique_code is generated once
                user_perk, created = UserPerk.objects.get_or_create(
                    user=request.user,
                    perk=perk,
                    is_used=False # Only show ones they haven't used yet
                )
                # Just append the user_perk; the template will handle the rest via 'perk' FK
                eligible_perks.append(user_perk)

        context.update({
            # offers
            "eligible_perks": eligible_perks,
        })

    # vouchers
    ledger_history = []

    if subpage == "vouchers":        
        # Extract Credits: Vouchers claimed by this user
        claimed_vouchers = CustomerVoucher.objects.filter(owner=request.user, is_claimed=True)
        for v in claimed_vouchers:
            ledger_history.append({
                "date": v.claimed_date if v.claimed_date else v.created_date,
                "summary": f"Gift voucher credit top-up｜充值禮品券面值金額 CNY ¥{v.value}<br/><span class='text-[0.65rem] opacity-60 font-mono'>ID: {str(v.id)[:8].upper()}...</span>",
                "amount": f"+RMB {v.value}",
                "amount_class": "text-success font-bold",
                "sort_date": v.claimed_date if v.claimed_date else v.created_date
            })

        # 3. Extract Debits: Voucher points spent on checkouts
        voucher_usages = OrderVoucherUsage.objects.filter(order__user=request.user).select_related('order', 'voucher')
        for u in voucher_usages:
            ledger_history.append({
                "date": u.created_at,
                "summary": f"Voucher usage for Order No｜使用禮品券額度於訂單號：<br/><span class='font-mono font-bold text-primary text-[8px] min-[401px]:max-[500px]:text-[9px] min-[501px]:max-[768px]:text-[11px] min-[769px]:text-xs'>{u.order.order_number}</span>",
                "amount": f"-RMB {u.amount_deducted}",
                "amount_class": "text-error font-bold",
                "sort_date": u.created_at
            })

        # 4. Chronological Pass: Sort all actions newest-to-oldest
        ledger_history.sort(key=lambda x: x["sort_date"], reverse=True)

        context.update({
            "page_title": subpage_title,
            "ledger_history": ledger_history,
        })

    # wishlist
    wishlist = None
    if subpage == "wishlist":
        wishlist = UserProductList.objects.filter(user=request.user, list_type="WISHLIST").order_by("-added_date")
        for wish in wishlist:
            wish.sku = wish.product_variation.get_sku()

        context.update({
            "wishlist": wishlist,
        })

    # favorites
    favorites = None
    if subpage == "favorites":
        favorites = UserProductList.objects.filter(user=request.user, list_type="FAVORITE").order_by("-added_date")
        for favorite in favorites:
            favorite.sku = favorite.product_variation.get_sku()

        context.update({
            "favorites": favorites,
        })

    # help
    if subpage == "help":
        admin_user = Account.objects.filter(is_superadmin=True).first()
        user = request.user
        
        # Get search query
        search_query = request.GET.get('q', '').strip()
        
        # Initialize with empty messages
        chat_messages = ChatMessage.objects.none()
        other_user = None
        
        if user.is_superadmin:
            # Admin: Start with NO messages loaded - wait for member selection
            members = Account.objects.filter(is_superadmin=False)
            
            # Calculate unread counts for each member
            for member in members:
                member.unread_count = ChatMessage.objects.filter(
                    sender=member,
                    receiver=user,
                    is_read=False
                ).count()
            
            # Total unread count
            unread_count = ChatMessage.objects.filter(
                receiver=user,
                is_read=False
            ).count()
            
            context["members"] = members
            
            # Check if there's a session-stored member selection
            member_id = request.session.get('chat_member_id')
            if member_id and not request.headers.get('HX-Request'):
                # Only load on initial page load, not on HTMX requests
                # Actually, let's not load any messages initially
                request.session.pop('chat_member_id', None)
            
        else:
            # Regular user: Load conversation with admin immediately
            other_user = admin_user
            chat_messages = ChatMessage.objects.filter(
                (Q(sender=other_user) & Q(receiver=user)) |
                (Q(sender=user) & Q(receiver=other_user))
            ).order_by("timestamp")
            
            # Apply search filter if query exists
            if search_query:
                chat_messages = chat_messages.filter(
                    Q(content__icontains=search_query) |
                    Q(sender__username__icontains=search_query)
                )
                
                # Add highlighting to search results
                import re
                from django.utils.safestring import mark_safe
                
                pattern = re.compile(f'({re.escape(search_query)})(?![^<]*>)', re.IGNORECASE)
                for msg in chat_messages:
                    msg.is_match = True
                    msg.highlighted_text = mark_safe(
                        pattern.sub(r'<span class="search-hit">\1</span>', msg.content)
                    )
        
        # Find first unread message (only for non-admin)
        first_unread = None
        if other_user and not user.is_superadmin:
            first_unread = ChatMessage.objects.filter(
                receiver=user,
                sender=other_user,
                is_read=False
            ).order_by('timestamp').first()

        print("chat_messages: ", chat_messages)
        context.update({
            "chat_messages": chat_messages,
            "admin": admin_user,
            "other_user": other_user,
            "first_unread_id": first_unread.id if first_unread else None,
            "search_query": search_query,
        })

    # Global layout branding strings
    context.update({
        "page_title": f"Member Hub｜我的中心控台 - {subpage_title}",
        "main_title": f"Hi｜你好, {request.user.username}!",
        "sub_title_1": "Your Exclusive Space｜您的專屬空間",
        "sub_title_2": f"{subpage_title}",
    })

    # 🌟 FIX HTMX INTERCEPT ROUTER TARGETS SAFELY
    if request.headers.get('HX-Request'):
        if request.headers.get('HX-Target') == "chat_message_list":
            # Check session values directly instead of using dangling tracking flags
            if request.user.is_superadmin and request.session.get('chat_member_id'):
                template = "accounts/partials/admin_chat_list.html"
            else:
                template = "accounts/partials/chat_list.html"
            return render(request, template, context)

        # Standard sidebar navigation request (clicking a sidebar link swap)
        response = render(request, template_name, context)
        response['HX-Title'] = subpage_title
        response['HX-Trigger'] = json.dumps({
            "updateBannerSubTitle": {
                "sub_title_2": context.get("sub_title_2", ""),
            }
        })
        return response
    
    return render(request, "accounts/dashboard.html", context)


def get_profile_strength(request):
    return render(request, 'accounts/partials/profile_strength_inner.html')


def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, profile=request.user.profile)
    initial_data = {}
    if address.country == 'CN':
        initial_data['china_province'] = address.state_province_region

    has_saved_addresses = Address.objects.filter(profile=request.user.profile).exists()
    
    address_book_form = AddressBookForm(instance=address, initial=initial_data)
    
    return render(request, 'accounts/partials/address_form.html', {
        'address_book_form': address_book_form,
        'address': address,
        'submit_btn': "Update｜更&nbsp;新",
        'has_saved_addresses': has_saved_addresses
    })


def update_address(request, pk):
    # Ensure the user owns this address
    address = get_object_or_404(Address, pk=pk, profile=request.user.profile)
    
    # 🌟 SURGICAL SAVE SAFEGUARD: Cache the original default status from database indexes
    was_default = address.is_default 
    
    if request.method == "POST":
        form = AddressBookForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if not address.address_line_1:
                address.is_verified_by_google = False                            
            if address.country == 'CN':
                address.state_province_region = form.cleaned_data.get('china_province')
            
            # 🌟 HARDEN FLAG INTEGRITY: Enforce original default status if it was dropped 
            # by form exclusions or unchecked checkbox missing payloads
            if was_default:
                address.is_default = True
                
            address.save() # Commit changes securely to the model layer
            
            # 1. Fetch updated list to re-render the address card grid
            user_addresses = Address.objects.filter(profile=request.user.profile)
            
            # main target
            list_html = render_to_string('accounts/partials/address_list_partial.html', {
                'user_addresses': user_addresses
            }, request=request)

            # sidebar
            sidebar_html = render_to_string('accounts/partials/profile_strength_display.html', {
                'user': request.user
            }, request=request)

            # combined
            combined_html = list_html + sidebar_html
            response = HttpResponse(combined_html)
            
            # 3. Trigger a client-side event to close the modal
            response['HX-Trigger'] = json.dumps({
                "addressSaved": {
                    "closeModal": "my_modal_2",
                },
                "addressUpdated": True
            })
            return response
        else:
            response = render(request, 'accounts/partials/address_form.html', {
                'address_book_form': form,
                'address': address, 
                'submit_btn': "Update｜更&nbsp;新",
                'has_saved_addresses': True # 🌟 Keep form checkbox rendering consistent on error fallback paths
            })
            response['HX-Retarget'] = '#modal_content_area'
            return response
            
    return HttpResponse(status=405)


def create_address(request):
    if request.method == "POST":
        address_book_form = AddressBookForm(request.POST)
        if address_book_form.is_valid():
            address = address_book_form.save(commit=False)
            if not address.address_line_1:
                address.is_verified_by_google = False                            
            if address.country == 'CN':
                address.state_province_region = address_book_form.cleaned_data.get('china_province')
            address.profile = request.user.profile
            address.save()

            # 1. Fetch updated list to re-render the address card grid
            user_addresses = Address.objects.filter(profile=request.user.profile)

            # Render ONLY the clean list items directly into the targeted #address-list-container
            list_html = render_to_string('accounts/partials/address_list_partial.html', {
                'user_addresses': user_addresses
            }, request=request)

            sidebar_html = render_to_string('accounts/partials/profile_strength_display.html', {
                'user': request.user
            }, request=request)

            combined_html = list_html + sidebar_html
            response = HttpResponse(combined_html)
            
            # 🌟 THE UNIFIED SOLUTION: Dispatch native lifecycle bridges directly into your DOM
            # This triggers your built-in SweetAlert toast and instantly shuts 'my_modal_1' cleanly!
            response['HX-Trigger'] = json.dumps({
                "addressCreated": True,
                "addressSaved": {
                    "closeModal": "my_modal_1"
                }
            })
            return response
        else:
            has_saved_addresses = Address.objects.filter(profile=request.user.profile).exists()
            response = render(request, 'accounts/partials/address_form.html', {
                'address_book_form': address_book_form,
                'submit_btn': "Create｜新&nbsp;增",
                'has_saved_addresses': has_saved_addresses
            })
            response['HX-Retarget'] = '#create_address_modal_content_area'
            return response
    return HttpResponse(status=405)


def delete_address(request, pk):
    if request.method == "POST":
        address = get_object_or_404(Address, pk=pk, profile=request.user.profile)
        address.delete()

        # Fetch the updated list to re-render the address card grid
        user_addresses = Address.objects.filter(profile=request.user.profile)

        # main target
        list_html = render_to_string('accounts/partials/address_list_partial.html', {
            'user_addresses': user_addresses
        }, request=request)

        # sidebar
        sidebar_html = render_to_string('accounts/partials/profile_strength_display.html', {
            'user': request.user
        }, request=request)

        combined_html = list_html + sidebar_html
        response = HttpResponse(combined_html)

        response['HX-Trigger'] = json.dumps({
            "addressDeleted": True
        })
        
        return response
    return HttpResponse(status=405)


def set_default_address(request, pk):
    """Sets target unique address instance default value to true natively."""
    if request.method == "POST":
        address = get_object_or_404(Address, pk=pk, profile=request.user.profile)
        address.is_default = True
        address.save() # Structural save logic handles wiping alternatives atomically
        
        # Pull dynamic entries collection to return a clean HTMX template loop response
        user_addresses = Address.objects.filter(profile=request.user.profile)
        
        list_html = render_to_string('accounts/partials/address_list_partial.html', {
            'user_addresses': user_addresses
        }, request=request)
        
        sidebar_html = render_to_string('accounts/partials/profile_strength_display.html', {
            'user': request.user
        }, request=request)

        combined_html = list_html + sidebar_html
        response = HttpResponse(combined_html)

        response['HX-Trigger'] = json.dumps({
            "addressDefaultSet": True
        })

        return response
    return HttpResponse(status=405)


def get_wishlist_item(request, item_id):
    item = get_object_or_404(UserProductList, id=item_id, user=request.user)
    return render(request, 'accounts/partials/wishlist_item.html', {'item': item})


@login_required(login_url='login')
def add_to_cart_qty(request, variation_id, source):
    """
    Fetches the targeted available product variation profile and maps context 
    dependencies safely based on source tracking matrices.
    """
    # 🌟 DATABASE PERFORMANCE OPTIMIZATION: Pull product attributes in a single row lock JOIN
    variation = get_object_or_404(
        ProductVariation.objects.select_related('product'), 
        id=variation_id, 
        is_available=True
    )
    
    list_item = None
    if source == "wishlist":
        list_item = variation.product_lists.filter(user=request.user, list_type="WISHLIST").first()
    elif source == "favorites":
        list_item = variation.product_lists.filter(user=request.user, list_type="FAVORITE").first()
        
    context = {
        'item': list_item,
        'variation': variation,
        'source': source,
    }
    return render(request, 'accounts/partials/item_qty_form.html', context)


@login_required
@require_POST
def add_to_cart_from_dashboard(request, variation_id):
    user = request.user
    variation = ProductVariation.objects.filter(pk=variation_id).first()
    cart_id = _cart_id(request)
    quantity = int(request.POST.get('quantity', 1))
    cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': cart_id})
    source = request.POST.get("source")
    triggers = {}

    if not variation.is_available:
        return htmx_unavailable_response(request, "Not Available｜已下架...", "Sorry, this item is no longer available...<br>抱歉，此款已下架...")
    elif variation.stock < 1:
        return htmx_unavailable_response(request, "Out of Stock｜已售罄", "Sorry, this item is temporarily out of stock.<br>抱歉，此產品暫時缺貨。")
    
    UserProductList.objects.filter(user=user, product_variation=variation, list_type='WISHLIST').delete()

    # check if already placed into cart via other pages
    existing_cart_item = CartItem.objects.filter(cart=cart, user=user, product_variation=variation).first()
    if existing_cart_item:
        cart_url = reverse('cart')
        triggers["infoMssg"] = { 
            "title": "Already in Cart｜已在您的購物車內",
            "html": f"Please view details in your <a href='{cart_url}'>cart</a> page.<br>請直接訪問您的<a href='{cart_url}'>購物車</a>頁面",
            "icon": "info"
        }
    else:
        if quantity > variation.stock:
            return htmx_unavailable_response(request, "Exceeds stock limit.｜超過庫存上限。", f"We’re sorry, only {variation.stock} items are currently available.｜很抱歉，目前僅剩 {variation.stock} 件存貨。", )
        
        CartItem.objects.create(user=user, cart=cart, product_variation=variation, quantity=quantity)
    
    # UI oobs
    updated_cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    context = {
        "current_cart_items": updated_cart_items,
        "is_htmx_update": True,
    }
    # header
    header_list_html = render_to_string("store/partials/header_cart_list.html", context, request=request)
    header_cart_summary_oob = update_header_cart_summary(cart)

    response = None
    if source == 'wishlist':
        # Update Wishlist
        wishlist = UserProductList.objects.filter(user=request.user, list_type="WISHLIST").order_by("-added_date")
        for wish in wishlist:
            wish.sku = wish.product_variation.get_sku()

        context["wishlist"] = wishlist

        # Render the main wishlist content (Targeted by hx-target="#wishlist_wrapper")
        main_html = render_to_string("accounts/partials/wishlist_item.html", context, request=request)
        response = HttpResponse(main_html + header_list_html + header_cart_summary_oob)

    elif source == 'favorites':
        # check if 
        response = HttpResponse(header_list_html + header_cart_summary_oob)

    response['HX-Trigger'] = json.dumps(triggers)
    return response
        

def check_stock(request, variation_id):
    variation = get_object_or_404(ProductVariation, id=variation_id)
    wishlist_item = variation.product_lists.filter(user=request.user, list_type="WISHLIST").first()
    variation.wishlist_item_id = wishlist_item.id if wishlist_item else None
    
    return render(request, 'accounts/partials/stock_badge.html', {'variation': variation})


@login_required(login_url="login")
@require_POST
def delete_favorite_item(request, item_id):
    favorite_item = UserProductList.objects.filter(pk=item_id, user=request.user, list_type="FAVORITE").first()
    need_broadcast = False

    if favorite_item:
        favorite_item.delete()
    elif not favorite_item:
        need_broadcast = True

    updated_favorites = UserProductList.objects.filter(user=request.user, list_type='FAVORITE')
    context = {"favorites": updated_favorites}

    response = render(request, 'accounts/partials/favorites_list.html', context)
    if need_broadcast:
        response["HX-Trigger"] = json.dumps({
            "infoMssg": {
               "title": "Item Removed | 項目已移除",
                "html": "This item was removed from your favorites in another tab.<br>此項目已在另一分頁中從收藏中移除。",
                "icon": "info"
            }
        })

    return response


@login_required(login_url="login")
@require_POST
def send_message(request):
    """Handle message sending - returns JSON for API or HTML for HTMX"""
    user = request.user
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content', '').strip()
    image = request.FILES.get('image')

    # Determine receiver
    admin_user = Account.objects.filter(is_superadmin=True).first()
    
    if user == admin_user:
        try:
            receiver = Account.objects.get(pk=receiver_id)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'Receiver not found'}, status=404)
    else:
        receiver = admin_user

    if not content and not image:
        return JsonResponse({'error': 'Content is required'}, status=400)

    if not admin_user:
        return JsonResponse({'error': 'System Admin not found'}, status=404)
    
    # Create message
    new_message = ChatMessage.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content,
        image=image,
    )
    
    # Send WebSocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_notifications_{receiver.id}",
        {
            "type": "chat_notification",
            "msg_id": new_message.id,
            "receiver_id": new_message.receiver.id,
            "sender_id": request.user.id,
            "sender_name": request.user.username,
            "sender_avatar_url": request.user.profile.profile_picture.url,
            "msg_content": new_message.content,
            "msg_img_url": new_message.image.url if new_message.image else None,
            "msg_timestamp": new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
    )
    
    # Check if this is an API request (fetch) or HTMX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
        # Return JSON for API
        return JsonResponse({
            'id': new_message.id,
            'sender_id': new_message.sender.id,
            'sender_name': new_message.sender.username,
            'sender_avatar': new_message.sender.profile.profile_picture.url,
            'content': format_chat(new_message.content),
            'image_url': new_message.image.url if new_message.image else None,
            'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': new_message.is_read,
        })
    else:
        # Return HTML for HTMX
        context = {
            "new_message": new_message,
            "admin": admin_user
        }
        return render(request, 'accounts/partials/new_chat_mssg.html', context)

def refresh_chat(request):
    msg_id = request.GET.get('msg_id')
    
    # Safety Check: If msg_id is missing or "undefined"
    if not msg_id or msg_id == "undefined":
        return HttpResponse(status=204) # Return empty "No Content" response

    try:
        new_message = ChatMessage.objects.get(id=msg_id)
    except ChatMessage.DoesNotExist:
        # If the DB hasn't saved it yet, return empty. 
        # The WebSocket usually retries or the user sees it on next load.
        return HttpResponse(status=204)

    admin_user = Account.objects.filter(is_superadmin=True).first()
    search_query = request.GET.get('q', '').strip()

    # Apply highlighting logic for search consistency
    if search_query and search_query.lower() in new_message.content.lower():
        pattern = re.compile(f'({re.escape(search_query)})(?![^<]*>)', re.IGNORECASE)
        new_message.is_match = True
        new_message.highlighted_text = mark_safe(
            pattern.sub(r'<span class="bg-warning text-dark search-hit">\1</span>', new_message.content)
        )

    # ✅ Get updated unread count
    unread_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()

    context = {
        "new_message": new_message,
        "admin": admin_user,
        "unread_count": unread_count,
    }

    # ✅ Also return OOB updates for badges
    response = render(request, "accounts/partials/new_chat_mssg.html", context)

    # Add OOB swap for unread count badges
    oob_html = f'''
        <span id="unread-count-header" hx-swap-oob="true">{unread_count}</span>
        <span id="unread-count-sidebar" hx-swap-oob="true">{unread_count}</span>
    '''
    response.content = response.content + oob_html.encode()
    
    return response    


@login_required(login_url='login')
def filter_message_by_member(request, member_id):
    """Load conversation with specific member for admin"""
    print(f"=== DEBUG: filter_message_by_member called ===")
    print(f"Request path: {request.path}")
    
    admin = request.user
    
    if not admin.is_superadmin:
        print("Not admin, returning 403")
        return HttpResponse(status=403)
    
    try:
        member = Account.objects.get(pk=member_id, is_superadmin=False)
        print(f"Member found: {member.username}")
    except Account.DoesNotExist:
        print(f"Member {member_id} not found")
        return HttpResponse("<div class='text-center text-white/50 py-10'>Member not found</div>")
    
    # Get ALL messages for this conversation
    all_messages = ChatMessage.objects.filter(
        (Q(sender=member) & Q(receiver=admin)) |
        (Q(sender=admin) & Q(receiver=member))
    ).order_by("timestamp")
    
    total_count = all_messages.count()
    print(f"Total messages found: {total_count}")
    
    # Pagination - show last 50 messages initially
    page_size = 50
    messages_to_show = all_messages[max(0, total_count - page_size):]
    
    # Mark messages as read
    ChatMessage.objects.filter(
        sender=member,
        receiver=admin,
        is_read=False
    ).update(is_read=True)
    
    context = {
        "chat_messages": messages_to_show,
        "member": member,
        "other_user": member,
        "admin": admin,
        "first_unread_id": None,
        "total_messages": total_count,
        "shown_messages": messages_to_show.count(),
    }
    
    request.session['chat_member_id'] = member_id
    request.session.modified = True
    
    response = render(request, "accounts/partials/admin_chat_list.html", context)
    response['HX-Trigger-After-Swap'] = 'chatLoaded'
    print("=== DEBUG: Response rendered successfully ===")
    return response


@login_required(login_url='login')
def load_all_messages(request, member_id):
    """Load all messages for a specific member conversation"""
    admin = request.user
    
    if not admin.is_superadmin:
        return HttpResponse(status=403)
    
    try:
        member = Account.objects.get(pk=member_id, is_superadmin=False)
    except Account.DoesNotExist:
        return HttpResponse("<div class='text-center text-white/50 py-10'>Member not found</div>")
    
    # Get ALL messages
    all_messages = ChatMessage.objects.filter(
        (Q(sender=member) & Q(receiver=admin)) |
        (Q(sender=admin) & Q(receiver=member))
    ).order_by("timestamp")
    
    context = {
        "chat_messages": all_messages,
        "member": member,
        "other_user": member,
        "admin": admin,
        "first_unread_id": None,
        "total_messages": all_messages.count(),
        "shown_messages": all_messages.count(),
    }
    
    request.session['chat_member_id'] = member_id
    
    response = render(request, "accounts/partials/admin_chat_list.html", context)
    response['HX-Trigger-After-Swap'] = 'chatLoaded'
    return response


@require_POST
def mark_read(request, msg_id):
    admin = Account.objects.filter(is_superadmin=True).first()
    msg = get_object_or_404(ChatMessage, id=msg_id, receiver=request.user)
    msg.is_read = True
    msg.save()

    return HttpResponse(status=204)        


def get_unread_count(request, sender_id=None):
    receiver = request.user

    # Mark all messages as read
    if request.GET.get('mark_read') == 'true':
        ChatMessage.objects.filter(receiver=receiver, is_read=False).update(is_read=True)

    # Total count
    unread_msgs_count_total = ChatMessage.objects.filter(
        receiver=receiver, is_read=False
    ).count()

    # Specific member count (for Admin view)
    if sender_id:
        count = ChatMessage.objects.filter(
            sender_id=sender_id, receiver=receiver, is_read=False
        ).count()
        return HttpResponse(str(count))
    
    # Return JSON if requested
    if request.GET.get('format') == 'json':
        return JsonResponse({'unread_count': unread_msgs_count_total})
    
    # Return OOB HTML for HTMX
    html = f'<span id="unread-count-header" hx-swap-oob="true">{unread_msgs_count_total}</span>'
    html += f'<span id="unread-count-sidebar" hx-swap-oob="true">{unread_msgs_count_total}</span>'
    
    return HttpResponse(html)


@login_required(login_url='login')
@require_GET
def api_conversation(request, member_id):
    """API endpoint for loading conversation messages"""
    admin = request.user
    
    if not admin.is_superadmin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        member = Account.objects.get(pk=member_id, is_superadmin=False)
    except Account.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)
    
    limit = int(request.GET.get('limit', 50))
    
    messages = ChatMessage.objects.filter(
        (Q(sender=member) & Q(receiver=admin)) |
        (Q(sender=admin) & Q(receiver=member))
    ).order_by("timestamp")
    
    total_count = messages.count()
    messages = messages[max(0, total_count - limit):]
    
    # Mark as read
    ChatMessage.objects.filter(
        sender=member,
        receiver=admin,
        is_read=False
    ).update(is_read=True)
    
    # Get updated unread counts
    unread_count = ChatMessage.objects.filter(
        receiver=admin,
        is_read=False
    ).count()
    
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.username,
        'sender_avatar': msg.sender.profile.profile_picture.url,
        'content': format_chat(msg.content),
        'image_url': msg.image.url if msg.image else None,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': msg.is_read,
    } for msg in messages]
    
    return JsonResponse({
        'messages': messages_data,
        'total_count': total_count,
        'unread_count': unread_count,
    })


@login_required(login_url='login')
@require_GET
def api_search_messages(request):
    """API endpoint for searching messages in a conversation"""
    search_query = request.GET.get('q', '').strip()
    receiver_id = request.GET.get('receiver_id', '')
    
    user = request.user
    
    if not search_query:
        return JsonResponse({'messages': [], 'total_count': 0})
    
    # Determine the conversation partner
    if user.is_superadmin:
        # Admin searching within a specific member's conversation
        if not receiver_id:
            return JsonResponse({'error': 'Receiver ID required'}, status=400)
        
        try:
            other_user = Account.objects.get(pk=receiver_id, is_superadmin=False)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)
    else:
        # Regular user searching within admin conversation
        other_user = Account.objects.filter(is_superadmin=True).first()
        if not other_user:
            return JsonResponse({'error': 'Admin not found'}, status=404)
    
    # Search messages
    chat_messages = ChatMessage.objects.filter(
        (Q(sender=other_user) & Q(receiver=user)) |
        (Q(sender=user) & Q(receiver=other_user))
    ).filter(
        Q(content__icontains=search_query) |
        Q(sender__username__icontains=search_query)
    ).order_by("timestamp")
    
    total_count = chat_messages.count()
    
    # Build response data
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.username,
        'sender_avatar': msg.sender.profile.profile_picture.url,
        'content': format_chat(msg.content),
        'image_url': msg.image.url if msg.image else None,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': msg.is_read,
    } for msg in chat_messages]
    
    return JsonResponse({
        'messages': messages_data,
        'total_count': total_count,
        'query': search_query,
    })


@login_required(login_url='login')
@require_GET
def api_my_conversation(request):
    """API endpoint for non-admin users to load their conversation with admin"""
    user = request.user
    
    if user.is_superadmin:
        return JsonResponse({'error': 'Use admin endpoint'}, status=400)
    
    admin_user = Account.objects.filter(is_superadmin=True).first()
    
    if not admin_user:
        return JsonResponse({'error': 'Admin not found'}, status=404)
    
    limit = int(request.GET.get('limit', 50))
    
    messages = ChatMessage.objects.filter(
        (Q(sender=admin_user) & Q(receiver=user)) |
        (Q(sender=user) & Q(receiver=admin_user))
    ).order_by("timestamp")
    
    total_count = messages.count()
    messages = messages[max(0, total_count - limit):]
    
    # Mark as read
    ChatMessage.objects.filter(
        sender=admin_user,
        receiver=user,
        is_read=False
    ).update(is_read=True)
    
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.username,
        'sender_avatar': msg.sender.profile.profile_picture.url,
        'content': format_chat(msg.content),
        'image_url': msg.image.url if msg.image else None,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': msg.is_read,
    } for msg in messages]
    
    return JsonResponse({
        'messages': messages_data,
        'total_count': total_count,
    })


@login_required(login_url='login')
@require_POST
def api_mark_all_read(request):
    """Mark all messages as read for the current user"""
    user = request.user
    
    # Check if we need to mark only specific member's messages
    member_id = request.POST.get('member_id', '')
    
    if user.is_superadmin and member_id:
        # Admin: mark only messages from specific member
        updated = ChatMessage.objects.filter(
            sender_id=member_id,
            receiver=user,
            is_read=False
        ).update(is_read=True)
    else:
        # Mark all messages as read
        updated = ChatMessage.objects.filter(
            receiver=user,
            is_read=False
        ).update(is_read=True)
    
    # Get updated total unread count
    total_unread = ChatMessage.objects.filter(
        receiver=user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'status': 'success',
        'updated_count': updated,
        'total_unread': total_unread,
    })


# views.py
@login_required(login_url='login')
@require_GET
def api_get_all_unread_counts(request):
    """API endpoint to get unread counts for all members (admin only)"""
    user = request.user
    
    if not user.is_superadmin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get unread counts per member
    members = Account.objects.filter(is_superadmin=False)
    
    member_counts = []
    total_unread = 0
    
    for member in members:
        count = ChatMessage.objects.filter(
            sender=member,
            receiver=user,
            is_read=False
        ).count()
        
        total_unread += count
        member_counts.append({
            'member_id': member.id,
            'unread_count': count,
        })
    
    return JsonResponse({
        'total_unread': total_unread,
        'members': member_counts,
    })


@login_required(login_url='login')
def search_messages(request):
    """Search messages within the current conversation context"""
    search_query = request.GET.get('q', '').strip()
    receiver_id = request.GET.get('receiver_id', '')
    
    user = request.user
    admin_user = Account.objects.filter(is_superadmin=True).first()
    
    # If query is empty, return full conversation
    if not search_query:
        # Determine the conversation partner
        if user.is_superadmin:
            # Admin - reload selected member's conversation
            if receiver_id:
                try:
                    other_user = Account.objects.get(pk=receiver_id)
                except Account.DoesNotExist:
                    return HttpResponse(status=404)
            else:
                # No member selected, return empty
                return HttpResponse("<div class='text-center text-white/50 py-10'>Select a member to view conversation</div>")
        else:
            # Regular user - reload admin conversation
            other_user = admin_user
        
        # Get full conversation
        chat_messages = ChatMessage.objects.filter(
            (Q(sender=other_user) & Q(receiver=user)) |
            (Q(sender=user) & Q(receiver=other_user))
        ).order_by("timestamp")
        
    else:
        # Determine the conversation partner for search
        if user.is_superadmin:
            # Admin searching within a specific member's conversation
            if receiver_id:
                try:
                    other_user = Account.objects.get(pk=receiver_id)
                except Account.DoesNotExist:
                    return HttpResponse(status=404)
            else:
                # No specific member selected
                return HttpResponse(status=204)
        else:
            # Regular user searching within admin conversation
            other_user = admin_user
        
        # Filter messages for this conversation
        chat_messages = ChatMessage.objects.filter(
            (Q(sender=other_user) & Q(receiver=user)) |
            (Q(sender=user) & Q(receiver=other_user))
        ).filter(
            Q(content__icontains=search_query) |
            Q(sender__username__icontains=search_query)
        ).order_by("timestamp")
        
        # Add highlighting
        import re
        from django.utils.safestring import mark_safe
        
        pattern = re.compile(f'({re.escape(search_query)})(?![^<]*>)', re.IGNORECASE)
        for msg in chat_messages:
            msg.is_match = True
            msg.highlighted_text = mark_safe(
                pattern.sub(r'<span class="search-hit">\1</span>', msg.content)
            )
    
    context = {
        "chat_messages": chat_messages,
        "admin": admin_user,
        "other_user": other_user,
    }
    
    if user.is_superadmin:
        template = "accounts/partials/admin_chat_list.html"
    else:
        template = "accounts/partials/chat_list.html"
    
    return render(request, template, context)


@login_required(login_url='login')
@require_POST
def set_chat_member(request, member_id):
    """Set the active chat member for admin"""
    if not request.user.is_superadmin:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        member = Account.objects.get(pk=member_id, is_superadmin=False)
        request.session['chat_member_id'] = member_id
        return JsonResponse({'status': 'success'})
    except Account.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Member not found'}, status=404)


def load_earlier_messages(request):
    last_id = request.GET.get('last_id')
    other_user_id = request.GET.get('other_user_id')
    search_query = request.GET.get('q', '').strip()
    admin = Account.objects.filter(is_superadmin=True).first()

    is_hybrid = str(other_user_id) == str(request.user.id)

    if is_hybrid:
        query = Q(sender=admin) | Q(receiver=admin)
        other_user = admin
    else:
        other_user = get_object_or_404(Account, pk=other_user_id)
        query = (Q(sender=other_user) & Q(receiver=request.user)) | \
                (Q(sender=request.user) & Q(receiver=other_user))
        
    if search_query:
        query &= Q(content__icontains=search_query)

    earlier_messages_qs = ChatMessage.objects.filter(
        query,
        id__lt=last_id
    ).order_by('-timestamp')[:NUM_MSG_PER_LOAD]

    messages = list(reversed(earlier_messages_qs))

    if search_query:
        pattern = re.compile(f'({re.escape(search_query)})', re.IGNORECASE)
        for msg in messages:
            msg.is_match = True
            highlighted = pattern.sub(r'<span class="bg-warning text-dark search-hit">\1</span>', msg.content)
            msg.highlighted_text = mark_safe(highlighted)

    has_more = len(messages) == NUM_MSG_PER_LOAD

    context = {
        "chat_messages": messages,
        "admin": admin,
        "other_user": other_user,
        "has_more": has_more,
        "search_query": search_query,
    }

    # ✅ Render the wrapper template
    return render(request, "accounts/partials/earlier_messages_wrapper.html", context)


@login_required(login_url='login')
def get_message_fragment(request, member_id):
    """Return only the message items for a conversation"""
    admin = request.user
    
    if not admin.is_superadmin:
        return HttpResponse(status=403)
    
    try:
        member = Account.objects.get(pk=member_id, is_superadmin=False)
    except Account.DoesNotExist:
        return HttpResponse("<div class='text-center text-white/50 py-10'>Member not found</div>")
    
    # Get the last 50 messages
    all_messages = ChatMessage.objects.filter(
        (Q(sender=member) & Q(receiver=admin)) |
        (Q(sender=admin) & Q(receiver=member))
    ).order_by("timestamp")
    
    total_count = all_messages.count()
    messages_to_show = all_messages[max(0, total_count - 50):]
    
    # Mark as read
    ChatMessage.objects.filter(
        sender=member,
        receiver=admin,
        is_read=False
    ).update(is_read=True)
    
    context = {
        "chat_messages": messages_to_show,
        "member": member,
        "other_user": member,
        "admin": admin,
        "total_messages": total_count,
        "shown_messages": messages_to_show.count(),
    }
    
    # Return ONLY the message items, no wrapper
    return render(request, "accounts/partials/admin_chat_messages_only.html", context)





def wishlist(request):
    user = request.user
    wishlist = UserProductList.objects.filter(user=user, list_type="WISHLIST").order_by("-added_date")
    for wish in wishlist:
        wish.sku = wish.product_variation.get_sku()

    wishlist_json = {}
    for wish in wishlist:
        wishlist_json[wish.product_variation.id] = {
            "sku": wish.sku,
            "product_name": wish.product_variation.product.product_name,
            "product_price": str(wish.product_variation.price),
            "product_url": f"/store/product/{wish.product_variation.product.category.slug}/{wish.product_variation.product.slug}",
            "product_image": wish.product_variation.images.url,
            "product_variation_stock": wish.product_variation.stock
        }

    context = {
        "page_title": "Member-Wishlist｜會員-未來購物清單",
        "main_title": f"Hi｜您好,{user.username}!",
        "sub_title_1": "Here is your wishlist｜這是您的未來購物計劃清單❤️",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Members｜會員",
        "bread_crumb_3": "Wishlist｜未來購物清單",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/accounts/dashboard",
        "bread_crumb_3_url": "/accounts/dashboard/wishlist",
        "wishlist": wishlist if wishlist else None,
        "wishlist_json": wishlist_json,
    }

    return render(request, "accounts/dashboard_wishlist.html", context)


def firework(request):
    return render(request, "accounts/three/firework.html")


def claim_voucher_routing_view(request, voucher_id):
    """
    Polymorphic Multi-Step State Engine:
    Step 1: Renders landing details and account ownership confirmation gates.
    Step 2: Handles async/HTMX PIN generation to the registered_email channel.
    Step 3: Validates PIN and executes final atomic wallet credit settlement.
    """
    try:
        voucher = CustomerVoucher.objects.get(id=voucher_id)
    except (CustomerVoucher.DoesNotExist, ObjectDoesNotExist):
        # Render a premium, localized, user-friendly cancellation landing page instead of a hard 404 error!
        context = {
            "page_title": "Voucher Unavailable｜禮品券不可用",
            "error_headline": "Voucher Cancelled or Unavailable｜該禮品券已註銷或不存在",
            "error_message": "This gift voucher link is no longer active. It may have been canceled due to a dynamic transaction reversal, order refund, or data administrative restructurings.",
            "error_message_cn": "此禮品券連結目前已失效。可能由於相關訂單辦理了退款退貨、轉帳超時手續關閉、或系統後台數據異動而導致此代金券被取消註銷。"
        }
        return render(request, "pages/voucher_cancelled_notice.html", context, status=404)

    if voucher.is_claimed:
        messages.error(request, "此兌換券已被領取｜This gift voucher has already been claimed.")
        return redirect('home')

    associated_order = Order.objects.filter(recipient_email=voucher.registered_email).order_by('-created_at').first()
    gift_message = associated_order.gift_message if associated_order else ""
    
    # ── STEP 3: POST PROCESS VALIDAITON ROUTINE ───────────────────────
    if request.method == "POST" and "submit_pin" in request.POST:
        # Enforce account gate authentication first
        if not request.user.is_authenticated:
            messages.error(request, "請先登入帳戶以套用此代金券｜Authentication required.")
            return redirect('login')

        input_pin = request.POST.get("pin_code", "").strip()
        session_pin = request.session.get(f"claim_pin_{voucher.id}")
        attempts = request.session.get(f"claim_attempts_{voucher.id}", 0)

        if not session_pin:
            messages.error(request, "請先獲取驗證碼｜Please request a verification PIN first.")
            return redirect('claim_voucher_url', voucher_id=voucher.id)

        if input_pin != str(session_pin):
            attempts += 1
            request.session[f"claim_attempts_{voucher.id}"] = attempts
            request.session.modified = True

            if attempts >= 3:
                # Flush session token data to prevent further brute-force inputs
                request.session.pop(f"claim_pin_{voucher.id}", None)
                request.session.pop(f"claim_attempts_{voucher.id}", None)
                request.session.modified = True
                
                # Render failure block payload matching requirement
                context = {"voucher": voucher, "lockout": True}
                return render(request, "pages/claim_voucher.html", context)

            messages.error(request, f"驗證碼不正確，您還剩餘 {3 - attempts} 次機會｜Invalid PIN code.")
            return redirect('claim_voucher_url', voucher_id=voucher.id)

        # 🚀 ATOMIC EXECUTION SETTLEMENT PASS
        success = voucher.claim(request.user.email)
        if success:
            voucher.owner = request.user
            voucher.save()
            
            # Flush structural session state trackers cleanly
            request.session.pop(f"claim_pin_{voucher.id}", None)
            request.session.pop(f"claim_attempts_{voucher.id}", None)
            request.session.modified = True
            
            # Trigger 'SUCCESS' validation hook parameter to dashboard views
            return redirect('/accounts/dashboard/vouchers/?status=claimed_success')
        else:
            messages.error(request, "領取失敗，該禮券可能已被使用｜Claim processing exception.")
            return redirect('home')

    # ── STEP 2: HTMX/POST PIN DELIVERY SEQUENCE ──────────────────────
    if request.headers.get("HX-Request") and request.method == "POST":
        # Generate the single-use 6-digit cryptographic numeric token
        secure_pin = random.randint(100000, 999999)
        request.session[f"claim_pin_{voucher.id}"] = secure_pin
        request.session[f"claim_attempts_{voucher.id}"] = 0
        request.session.modified = True
        
        # 🌟 THE NET ARCHITECTURAL FIX: Trigger via Celery task queue!
        # This keeps the request completely non-blocking, responding to HTMX instantly.
        send_secure_voucher_pin_email_task.delay(str(voucher.id), str(secure_pin))

        # Swap out the inner HTML container elements cleanly using out-of-bound (OOB) markers
        response_html = f"""
        <div id="pin-interaction-container" hx-swap-oob="true" class="space-y-4 animate-fade-in">
            <div class="alert alert-success text-xs font-semibold text-white bg-teal-600 border-0">
                <i class="fa-solid fa-circle-check"></i>
                驗證碼已發送至您的郵箱 [{voucher.registered_email}]，請查收。
            </div>
            <div class="form-control">
                <label class="label text-xs font-bold text-base-content/70">Enter 6-Digit PIN｜請輸入6位數驗證碼</label>
                <input type="text" name="pin_code" maxlength="6" required class="input input-bordered text-center tracking-widest font-mono font-bold text-lg focus:outline-teal-600 focus:ring-0" placeholder="******" />
            </div>
            <button type="submit" name="submit_pin" class="w-full btn btn-neutral text-white">Verify & Claim Wallet Balance｜驗證並領取額度</button>
        </div>
        """
        return HttpResponse(response_html)

    # ── STEP 1: GET INITIAL LANDING VIEW RENDER ─────────────────────
    context = {
        "voucher": voucher,
        "gift_message": gift_message,
        "lockout": False,
        "page_title": "Claim Your Voucher｜領取您的電子禮卡"
    }
    return render(request, "pages/claim_voucher.html", context)
