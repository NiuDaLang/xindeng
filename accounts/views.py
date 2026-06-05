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
from carts.views import _cart_id
from django.db import transaction
from django.db.models import Q, Count
from django.utils.safestring import mark_safe
import re
from django.http import Http404

import uuid
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.urls import reverse
from carts.utils import update_header_cart_summary

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

NUM_MSG_PER_LOAD = 10


# Create your views here.
@sensitive_post_parameters("password", "password1", "password2")
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        receive_newsletter = form.cleaned_data["receive_newsletter"]
        password = form.cleaned_data["password1"]

        if form.is_valid():
            user = Account.objects.create_user(
                username=username,
                email=email,
                receive_newsletter=receive_newsletter,
                password=password, # Pass it here!
            )

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
        messages.success(request, "Account activated｜帳號已成功激活")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link｜激活連結無效")
        return redirect("register")
    

def login(request, user=None):
    if request.user.is_authenticated:
        return redirect("dashboard", subpage="main")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login successful｜登入成功")
            return redirect("dashboard", subpage="main")
        else:
            messages.error(request, "Login failed｜登入失敗")
            return redirect("login")
    
    return render(request, "pages/login.html")


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
        'profile': 'My Profile｜個人檔案',
        'addresses': 'Addresses｜地址簿',
        'orders': 'Orders｜購物紀錄',
        'offers': 'Offers｜福利活動',
        'vouchers': 'Vouchers｜禮品券',
        'wishlist': 'Wishlist｜購物清單',
        'favorites': 'Favorites｜收藏',
        'help': 'Help｜會員熱線',
        'threed': '3D Scenes｜三維場景',
    }
    template_name = templates.get(subpage, 'accounts/dashboard_main.html')
    subpage_title = page_title.get(subpage, 'Main｜管理主頁')
    chat_messages = ChatMessage.objects.none()
    search_query = request.GET.get('q', '').strip()
    active_member_id = request.session.get('chat_member_id')

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

    # addresses
    address_book_form = None
    user_addresses = None
    submit_btn = None
    if subpage == "addresses":
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_addresses = Address.objects.filter(profile=user_profile)
        address_book_form = AddressBookForm()
        submit_btn = "Create｜新&nbsp;增"
    
    # offers
    eligible_perks = None
    if subpage == "offers":
        all_active_perks = Perk.objects.filter(is_active=True)
        eligible_perks = []

        for perk in all_active_perks:
            print("perk: ", perk)
            status = PerkEvaluator.get_eligibility_status(request.user, perk)
            print("status, perk: ", status, perk)
            if status == 'VALID':
                # Using get_or_create is smart; it ensures the unique_code is generated once
                user_perk, created = UserPerk.objects.get_or_create(
                    user=request.user,
                    perk=perk,
                    is_used=False # Only show ones they haven't used yet
                )
                # Just append the user_perk; the template will handle the rest via 'perk' FK
                eligible_perks.append(user_perk)

    # wishlist
    wishlist = None
    if subpage == "wishlist":
        wishlist = UserProductList.objects.filter(user=request.user, list_type="WISHLIST").order_by("-added_date")
        for wish in wishlist:
            wish.sku = wish.product_variation.get_sku()

    # favorites
    favorites = None
    if subpage == "favorites":
        favorites = UserProductList.objects.filter(user=request.user, list_type="FAVORITE").order_by("-added_date")
        for favorite in favorites:
            favorite.sku = favorite.product_variation.get_sku()

    # help
    members = None
    admin = None
    other_user = None
    first_unread_id = None
    has_more = None
    unread_count = None
    if subpage == "help":
        admin = Account.objects.filter(is_superadmin=True).first()

        if not request.headers.get('HX-Request'):
            request.session.pop("chat_member_id", None)
            active_member_id = None
        
        # all-time chat history
        if active_member_id:
            other_user = get_object_or_404(Account, pk=active_member_id)
            messages_qs = ChatMessage.objects.filter(
                (Q(sender_id=active_member_id) & Q(receiver=request.user)) |
                (Q(sender=request.user) & Q(receiver_id=active_member_id))
            )
        else:
            other_user = admin if request.user != admin else request.user
            print('other user for hybrid and member: ', other_user)
            messages_qs = ChatMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user))

        if search_query:
            messages_qs = messages_qs.filter(content__icontains=search_query).order_by('-timestamp')
            chat_messages = list(reversed(messages_qs))
            pattern = re.compile(f'({re.escape(search_query)})(?![^<]*>)', re.IGNORECASE) # Look for the query only when it is not preceded by < or inside a tag
            for msg in chat_messages:
                msg.is_match = True
                # Use \1 to keep the original casing of the matched word
                highlighted = pattern.sub(r'<span class="bg-warning text-dark search-hit">\1</span>', msg.content)
                msg.highlighted_text = mark_safe(highlighted)
        else:
            unread_count = ChatMessage.objects.filter(
                receiver=request.user,
                is_read=False
            ).count()
        
            num_of_msg_per_load = max(NUM_MSG_PER_LOAD, unread_count+10)

            latest_msgs_qs = messages_qs.order_by("-timestamp")[:num_of_msg_per_load]

            chat_messages = list(reversed(latest_msgs_qs))

            total_count = messages_qs.count()

            has_more = total_count > num_of_msg_per_load

            first_unread = ChatMessage.objects.filter(
                receiver=request.user,
                is_read=False
            ).order_by('timestamp').first()

            first_unread_id = first_unread.id if first_unread else None

            members = Account.objects.filter(
                # Only get people who have sent a message that wasn't to the admin
                sent_messages__isnull=False
            ).exclude(
                id=admin.id
            ).annotate(
                # 2. Add a property 'unread_count' to each member
                # This counts messages where this member is the sender AND is_read is False
                unread_count=Count(
                    'sent_messages', 
                    filter=Q(sent_messages__is_read=False, sent_messages__receiver=admin)
                )
            ).distinct()    
       

    ### general ###
    # 節氣
    today = datetime.date.today()
    today_is_solar_term = check_today_is_solar_term(today)
    current_term, start_date = get_current_solar_term_period(today)
    trad_term, term_en, trad_next_term = None, None, None
    next_term, next_term_en = None, None
    translator = opencc.OpenCC('s2t.json')

    if current_term:
        trad_term = translator.convert(current_term)
        term_en = SOLAR[current_term]

    if not today_is_solar_term:
        next_term = get_next_solar_term(current_term)
        trad_next_term = translator.convert(next_term[0])
        next_term_en = next_term[1]

    context = {
        # main
        "subpage_template": template_name,
        "subpage": subpage,
        "user": request.user,
        "solar_term": trad_term,
        "solar_term_en": term_en,
        "next_solar_term": trad_next_term,
        "next_solar_term_en": next_term_en,

        # profile
        "user_profile": user_profile,
        "user_form": user_form,
        "profile_form": profile_form,
        "address_form": address_form,
        "user_form_errors": user_form_errors,
        "profile_form_errors": profile_form_errors,
        "address_form_errors": address_form_errors,

        # addresses
        "user_addresses": user_addresses,
        "address_book_form": address_book_form,
        "submit_btn": submit_btn,
        "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,

        # offers
        "eligible_perks": eligible_perks,

        # wishlist
        "wishlist": wishlist,

        # favorites
        "favorites": favorites,

        # help
        "chat_messages": chat_messages,
        "search_query": search_query,
        "admin": admin,
        "members": members,
        "first_unread_id": first_unread_id,
        "has_more": has_more,
        "unread_count": unread_count,
        "other_user": other_user,

        # banner
        "page_title": f"Member｜會員 - {subpage_title}",
        "main_title": f"Hi｜您好, {request.user.username}!",
        "sub_title_1": "Your Exclusive Space｜您的专属空间",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Member｜會員",
        "bread_crumb_3": subpage_title,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": f"/accounts/dashboard/main",
        "bread_crumb_3_url": f"/accounts/dashboard/{subpage}",
    }
    print("other_user: ", other_user)

    if request.headers.get('HX-Request'):
        if request.headers.get('HX-Target') == "chat_message_list":
            template = "accounts/partials/admin_chat_list.html" if active_member_id else "accounts/partials/chat_list.html"
            return render(request, template, context)
        
        # Otherwise, it's a subpage navigation request (clicking a sidebar link)
        response = render(request, template_name, context)
        response['HX-Title'] = subpage_title
        response['HX-Trigger'] = json.dumps({
            "updateBanner": {
                "title": context.get("bread_crumb_3", ""),
                "url": context.get("bread_crumb_3_url", "")
            }
        })
        return response

    return render(request, "accounts/dashboard.html", context)


def get_profile_strength(request):
    return render(request, 'accounts/partials/profile_strength_inner.html')


def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, profile=request.user.profile)
    
    # If it's a China address, pre-populate the china_province field for the form
    initial_data = {}
    if address.country == 'CN':
        initial_data['china_province'] = address.state_province_region
        
    address_book_form = AddressBookForm(instance=address, initial=initial_data)
    submit_btn = "Update｜更&nbsp;新"
    return render(request, 'accounts/partials/address_form.html', {
        'address_book_form': address_book_form, 
        'address': address, 
        'submit_btn': submit_btn
    })


def update_address(request, pk):
    # Ensure the user owns this address
    address = get_object_or_404(Address, pk=pk, profile=request.user.profile)
    
    if request.method == "POST":
        form = AddressBookForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if not address.address_line_1:
                address.is_verified_by_google = False                            
            if address.country == 'CN':
                address.state_province_region = form.cleaned_data.get('china_province')
            form.save()
            
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
            response = HttpResponse(list_html + sidebar_html)
            
            # 3. Trigger a client-side event to close the modal
            response['HX-Trigger'] = json.dumps({
                "addressSaved": {
                    "closeModal": "my_modal_2",
                }
            })
            return response
        else:
            response = render(request, 'accounts/partials/address_form.html', {
                'address_book_form': form, # Use 'address_book_form' to match template variable
                'address': address, 
                'submit_btn': "Update｜更&nbsp;新"
            })
            response['HX-Retarget'] = '#modal_content_area' # Send errors back to update modal
            return response
            
    return HttpResponse(status=405) # Method not allowed


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

            # main target
            list_html = render_to_string('accounts/partials/address_list_partial.html', {
                'user_addresses': user_addresses
            }, request=request)

            # sidebar
            sidebar_html = render_to_string('accounts/partials/profile_strength_display.html', {
                'user': request.user
            }, request=request)
            
            # combined
            response = HttpResponse(list_html + sidebar_html)
            
            # 3. Trigger a client-side event to close the modal
            response['HX-Trigger'] = json.dumps({
                "addressSaved": {
                    "closeModal": "my_modal_1",
                }
            })

            return response
        else:
            # Failure: Return the FORM to the list-container (HTMX will swap it there)
            # BUT: Since the target is the list-container, we have a problem.
            # Fix: Use "HX-Retarget" to send the errors back to the modal instead!
            response = render(request, 'accounts/partials/address_form.html', {
                'address_book_form': address_book_form,
                'submit_btn': "Create｜新&nbsp;增"
            })
            response['HX-Retarget'] = '#create_address_modal_content_area'
            return response
    return HttpResponse(status=405) # Method not allowed


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
        
        # combined
        response = HttpResponse(list_html + sidebar_html)
        
        # Render ONLY the card list partial
        return response


def get_wishlist_item(request, item_id):
    item = get_object_or_404(UserProductList, id=item_id, user=request.user)
    return render(request, 'accounts/partials/wishlist_item.html', {'item': item})


def add_to_cart_qty(request, variation_id, source):
    print("source in cart qty: ", source)
    # Get the variation and its related wishlist item for the current user
    variation = get_object_or_404(ProductVariation, id=variation_id, is_available=True)
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
    print("quantity: ", quantity, " source: ", source)

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
    user = request.user
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content', '').strip()
    image = request.FILES.get('image')

    # 1. Get the Admin account (the intended receiver)
    admin_user = Account.objects.filter(is_superadmin=True).first()
    if user == admin_user:
        receiver = Account.objects.get(pk=receiver_id)
    else:
        receiver = admin_user

    if not content:
        return HttpResponse("Content is required", status=400)

    if not admin_user:
        return HttpResponse("System Admin not found", status=404)
    
    new_message = ChatMessage.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content,
        image=image,
    )
    context = {
        "new_message": new_message,
        "admin": admin_user
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_notifications_{receiver.id}", # group_name
        {
            "type": "chat_notification",
            "msg_id": new_message.id,
            "receiver_id": new_message.receiver.id,
            "sender_id": request.user.id,
            "sender_name": request.user.username,
            "sender_avatar_url": request.user.profile.profile_picture.url,
            "msg_content": new_message.content, # Corrected key
            "msg_img_url": new_message.image.url if new_message.image else None,
            "msg_timestamp": new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
    )
    response = render(request, 'accounts/partials/new_chat_mssg.html', context)
    return response


# def refresh_chat(request):
#     msg_id = request.GET.get('msg_id')
#     new_message = ChatMessage.objects.get(id=msg_id)
#     admin_user = Account.objects.filter(is_superadmin=True).first()

#     search_query = request.GET.get('q', '').strip()
#     if search_query and search_query.lower() in new_message.content.lower():
#         pattern = re.compile(f'({re.escape(search_query)})', re.IGNORECASE)
#         new_message.is_match = True
#         new_message.highlighted_text = mark_safe(pattern.sub(r'<span class="bg-warning text-dark search-hit">\1</span>', new_message.content))

#     context = {
#         "new_message": new_message,
#         "admin": admin_user
#     }

#     return render(request, "accounts/partials/new_chat_mssg.html", context)

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

    context = {
        "new_message": new_message,
        "admin": admin_user
    }
    return render(request, "accounts/partials/new_chat_mssg.html", context)


def filter_message_by_member(request, member_id):
    admin = request.user
    member = get_object_or_404(Account, pk=member_id)

    unread_msgs_count_from_member = ChatMessage.objects.filter(
        receiver=admin,
        sender=member,
        is_read=False
    ).count()

    num_of_msg_per_load = max(NUM_MSG_PER_LOAD, unread_msgs_count_from_member+10)

    all_msgs_with_member = ChatMessage.objects.filter(
        (Q(sender=member) & Q(receiver=admin))|
        (Q(sender=admin) & Q(receiver=member))
    ).order_by("-timestamp")

    latest_msgs_qs = all_msgs_with_member[:num_of_msg_per_load]

    messages_with_member = list(reversed(latest_msgs_qs))

    total_msgs_count_from_member = ChatMessage.objects.filter(
        (Q(sender=member) & Q(receiver=admin))|
        (Q(sender=admin) & Q(receiver=member))
    ).count()

    has_more = total_msgs_count_from_member > num_of_msg_per_load # True or False

    first_unread = all_msgs_with_member.filter(
        receiver=request.user,
        is_read=False
    ).order_by('timestamp').first()

    context={
        "chat_messages": messages_with_member,
        "member": member,
        "other_user": member,
        "has_more": has_more,
        "first_unread_id": first_unread.id if first_unread else None
    }
    request.session['chat_member_id'] = member_id

    return render(request, "accounts/partials/admin_chat_list.html", context)


@require_POST
def mark_read(request, msg_id):
    admin = Account.objects.filter(is_superadmin=True).first()
    msg = get_object_or_404(ChatMessage, id=msg_id, receiver=request.user)
    print("mark read: ", msg.id, ": ", msg.content)
    msg.is_read = True
    msg.save()

    return HttpResponse(status=204)        


def get_unread_count(request, sender_id=None):
    receiver = request.user

    # 1. total count for anyone
    unread_msgs_count_total = ChatMessage.objects.filter(
        receiver=receiver, is_read=False
    ).count()

    # 3. specific member count (for Admin view)
    if sender_id:
        count = ChatMessage.objects.filter(
            sender_id=sender_id, receiver=receiver, is_read=False
        ).count()
        return HttpResponse(str(count))
    
    html = f'<span id="unread-count-header" hx-swap-oob="true">{unread_msgs_count_total}</span>'
    html += f'<span id="unread-count-sidebar" hx-swap-oob="true">{unread_msgs_count_total}</span>'
    
    return HttpResponse(html)


def load_earlier_messages(request):
    last_id = request.GET.get('last_id')
    other_user_id = request.GET.get('other_user_id')
    search_query = request.GET.get('q', '').strip()
    admin = Account.objects.filter(is_superadmin=True).first()

    is_hybrid = str(other_user_id) == str(request.user.id) # False

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
        id__lt=last_id # "less than" filter for older IDs
    ).order_by('-timestamp')[:NUM_MSG_PER_LOAD] # Get NUM_MSG_PER_LOAD, latest of the old ones first

    messages = list(reversed(earlier_messages_qs))

    # Apply highlighting logic
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

    return render(request, "accounts/partials/earlier_messages_wrapper.html", context)


def edit_order(request):
    user = request.user
    order_num = 'xxxxxxx'
    context = {
        "main_title": f"您好,{user}!",
        "sub_title_1": "XXXXX XXXXX",
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
        "sub_title_1": "XXXXX XXXXX",
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


def threed(request):
    user = request.user

    context = {
        "main_title": f"您好,{user}!",
        "sub_title_1": "XXXXX XXXXX",
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

