# creators/views.py
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Address, Account
from store.models import (
    Product, ProductGallery, ProductVariation, ProductReviewLog,
    ArtisanVaultUpload
)
from orders.models import OrderProduct, TrackingNumber

from .context import artisan_dashboard_context
from taggit.models import Tag

from .decorators import artisan_required
from .models import CreatorProfile, CraftType, ArtisanChatMessage
# If you go with Approach A:
from django.conf import settings
import os
from blog.models import Post, BlogPostReviewLog
from django.db.models import Q, Prefetch, Max, Count
from django.core.paginator import Paginator
from accounts.data import DESTINATIONS_MAINLAND_CHINA

from .utils import get_search_variants
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from .utils import stable_shuffle_queryset
import hashlib
from pathlib import Path
import uuid
import random
from datetime import datetime
from .forms import (
    ArtisanApplicationForm, 
    CreatorProfileForm, 
    BlogPostForm, 
    ArtisanVaultUploadForm
)
from orders.models import OrderProduct, TrackingNumber

from django.http import FileResponse, HttpResponse
from django.urls import reverse
from blog.tasks import send_blog_submission_email_task
from settlements.models import ArtisanSettlementLine

from store.forms import ArtisanProductForm, ProductVariationForm
from category.models import Category
from django_ckeditor_5.widgets import CKEditor5Widget
from django.http import JsonResponse
from django.http import Http404
import json

from store.tasks import (
    send_product_submission_email_task,
    send_product_deactivation_request_email_task,
    send_vault_upload_pending_email_task
)
import logging
logger = logging.getLogger(__name__)


PRODUCTS_PREVIEW_LIMIT = 8

# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC VIEWS — 匠人 Public-Facing Pages
# ═══════════════════════════════════════════════════════════════════════════

# def artisan_landing(request):
#     """
#     Hub page for 匠人 (Artisans). Hero with monthly atelier window,
#     featured artisans preview, recent works, join CTA.
#     """

#     # ── Featured artisans ─────────────────────────────────
#     featured_artisans = (
#         CreatorProfile.objects
#         .filter(is_verified=True)
#         .order_by('-is_premium', '-created_at')[:6]
#     )

#     # ── Featured products (recent artisan works) ──────────
#     featured_products = (
#         Product.objects
#         .filter(is_active=True, creator__is_verified=True)
#         .select_related('creator', 'category')
#         .order_by('-created_date')[:8]
#     )

#     # ── Monthly atelier clip ──────────────────────────────
#     current_month = timezone.now().month

#     monthly_clips = {
#         1:  {'file': 'atelier_january_calligraphy.mp4',  'title_en': 'Ink & Brush',     'title_cn': '揮毫迎歲'},
#         2:  {'file': 'atelier_february_embroidery.mp4',  'title_en': 'Silk & Thread',    'title_cn': '春絲如詩'},
#         3:  {'file': 'atelier_march_ceramics.mp4',       'title_en': 'Clay & Wheel',     'title_cn': '陶韻初醒'},
#         4:  {'file': 'atelier_april_bamboo.mp4',         'title_en': 'Bamboo & Knife',   'title_cn': '竹影清風'},
#         5:  {'file': 'atelier_may_inkwash.mp4',          'title_en': 'Ink Wash',         'title_cn': '墨染山河'},
#         6:  {'file': 'atelier_june_woodwork.mp4',        'title_en': 'Wood & Loom',      'title_cn': '機杼聲中'},
#         7:  {'file': 'atelier_july_jade.mp4',            'title_en': 'Jade & Stone',     'title_cn': '玉石細語'},
#         8:  {'file': 'atelier_august_lacquer.mp4',       'title_en': 'Lacquer',          'title_cn': '漆藝流光'},
#         9:  {'file': 'atelier_september_papercut.mp4',   'title_en': 'Paper & Cut',      'title_cn': '剪紙成詩'},
#         10: {'file': 'atelier_october_silver.mp4',       'title_en': 'Silver & Hammer',  'title_cn': '銀匠心事'},
#         11: {'file': 'atelier_november_teapot.mp4',      'title_en': 'Tea & Pot',        'title_cn': '茶香器韻'},
#         12: {'file': 'atelier_december_kiln.mp4',        'title_en': 'Fire & Glaze',     'title_cn': '窯火冬祭'},
#     }

#     current_clip = monthly_clips.get(current_month, {
#         'file': 'artisans_sample_clip.mp4',
#         'title_en': 'Atelier',
#         'title_cn': '匠人工坊',
#     })

#     # Build the media URL — fall back to sample if the specific month's file doesn't exist yet

#     monthly_file_path = os.path.join(
#         settings.MEDIA_ROOT,
#         'artisans', 'hero', current_clip['file']
#     )

#     if not os.path.exists(monthly_file_path):
#         # Fallback to the sample clip until the monthly assets are ready
#         current_clip = {
#             'file': 'artisans_sample_clip.mp4',
#             'title_en': 'Atelier',
#             'title_cn': '匠人工坊',
#         }

#     current_clip['video_url'] = f"{settings.MEDIA_URL}artisans/hero/{current_clip['file']}"

#     # 🌟 Recent artisan-authored blog posts
#     recent_artisan_posts = (
#         Post.objects
#         .filter(
#             status='Published',
#             creator__isnull=False,
#             creator__is_verified=True,
#         )
#         .select_related('creator')
#         .order_by('-created_at')[:3]
#     )

#     context = {
#         'featured_artisans': featured_artisans,
#         'featured_products': featured_products,
#         'recent_artisan_posts': recent_artisan_posts, 
#         'current_clip': current_clip,
#         'page_title': 'Artisans｜匠人',
#         'main_title': 'Soul of Craft｜匠心之魂',
#         'sub_title_1': 'Where Timeless Art Meets Modern Life｜古老手藝，當代心燈',
#     }
#     return render(request, 'artisans/artisan_landing.html', context)


def artisan_landing(request):
    """
    Hub page for 匠人 (Artisans). Hero with monthly atelier window,
    featured artisans preview, recent works, join CTA.
    """
    from django.contrib.staticfiles import finders
    from django.templatetags.static import static

    # ── Featured artisans ─────────────────────────────────
    featured_artisans = (
        CreatorProfile.objects
        .filter(is_verified=True)
        .order_by('-is_premium', '-created_at')[:6]
    )

    # ── Featured products (recent artisan works) ──────────
    featured_products = (
        Product.objects
        .filter(is_active=True, creator__is_verified=True)
        .select_related('creator', 'category')
        .order_by('-created_date')[:8]
    )

    # ── Monthly atelier clip ──────────────────────────────
    current_month = timezone.now().month

    monthly_clips = {
        1:  {'file': 'atelier_january_calligraphy.mp4',  'title_en': 'Ink & Brush',     'title_cn': '揮毫迎歲'},
        # ... (unchanged)
        12: {'file': 'atelier_december_kiln.mp4',        'title_en': 'Fire & Glaze',     'title_cn': '窯火冬祭'},
    }

    FALLBACK_CLIP = {
        'file': 'artisans_sample_clip.mp4',
        'title_en': 'Atelier',
        'title_cn': '匠人工坊',
    }

    current_clip = dict(monthly_clips.get(current_month, FALLBACK_CLIP))

    # If the specific month's clip doesn't exist yet, fall back to the sample.
    # finders.find() checks all STATICFILES_DIRS, not MEDIA_ROOT.
    if not finders.find(f"artisans/hero/{current_clip['file']}"):
        current_clip = dict(FALLBACK_CLIP)

    # ── Recent artisan-authored blog posts ────────────────
    recent_artisan_posts = (
        Post.objects
        .filter(
            status='Published',
            creator__isnull=False,
            creator__is_verified=True,
        )
        .select_related('creator')
        .order_by('-created_at')[:3]
    )

    context = {
        'featured_artisans': featured_artisans,
        'featured_products': featured_products,
        'recent_artisan_posts': recent_artisan_posts,
        'current_clip': current_clip,
        'current_clip_url': static(f"artisans/hero/{current_clip['file']}"),
        'page_title': 'Artisans｜匠人',
        'main_title': 'Soul of Craft｜匠心之魂',
        'sub_title_1': 'Where Timeless Art Meets Modern Life｜古老手藝，當代心燈',
    }
    return render(request, 'artisans/artisan_landing.html', context)


def artisan_list(request):
    """
    Profiles page (匠心). Grid of artisan cards with search + craft + province filters.
    HTMX-enabled filters that swap only the grid.
    """
    qs = CreatorProfile.objects.filter(is_verified=True)

    # ── SEARCH ────────────────────────────────────────
    q = request.GET.get('q', '').strip()
    if q:
        variants = get_search_variants(q)
        # Build an OR query that matches any variant
        variant_q = Q()
        for v in variants:
            variant_q |= (
                Q(display_name__icontains=v) |
                Q(tagline__icontains=v) |
                Q(bio__icontains=v) |
                Q(province__icontains=v) |
                Q(city__icontains=v) |
                Q(craft_types__name__icontains=v) | 
                Q(craft_types__label__icontains=v) |
                Q(tags__name__icontains=v)
            )
        qs = qs.filter(variant_q).distinct()

    # ── CRAFT FILTER ──────────────────────────────────
    craft = request.GET.get('craft', '').strip()
    if craft:
        qs = qs.filter(craft_types__name=craft).distinct()

    # ── PROVINCE FILTER ───────────────────────────────
    province = request.GET.get('province', '').strip()
    if province:
        qs = qs.filter(province=province)

    # Premium first, then alphabetical within tier
    qs = qs.order_by('-is_premium', 'display_name')

    paginator = Paginator(qs, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Distinct provinces for the province dropdown — only from verified artisans
    provinces = (
        CreatorProfile.objects
        .filter(is_verified=True)
        .exclude(province='')
        .values_list('province', flat=True)
        .distinct()
        .order_by('province')
    )

    # Map province keys to bilingual display labels
    province_labels = dict(DESTINATIONS_MAINLAND_CHINA)
    current_province_label = province_labels.get(province, province) if province else ''

    context = {
        'page_obj': page_obj,
        'artisans': page_obj,
        'craft_choices': CraftType.objects.all(),
        'provinces': provinces,
        'province_labels': province_labels,
        'current_province_label': current_province_label,
        'current_q': q,
        'current_craft': craft,
        'current_province': province,
        'page_title': 'Artisan Profiles｜匠心',
        'main_title': 'Artisan Profiles｜匠心',
        'sub_title_1': 'Each heart, a story. Each hand, a signature.',
        'sub_title_2': '每一顆匠心，都是一則故事；每一雙手，都有獨特的印記。',
        'bread_crumb_1': 'Home｜首頁',
        'bread_crumb_2': 'Artisans｜匠人',
        'bread_crumb_3': 'Profiles｜匠心',
        'bread_crumb_1_url': '/',
        'bread_crumb_2_url': '/artisans/',
        'bread_crumb_3_url': '/artisans/profiles/',
    }

    # HTMX intercept — return only the grid partial
    if request.headers.get('HX-Request'):
        return render(request, 'artisans/partials/_artisan_filter_region.html', context)

    return render(request, 'artisans/artisan_list.html', context)


def resolve_artisan_template(artisan):
    """
    Returns the template path for the artisan's public page.
    Priority:
    1. Custom premium template (D) if published and file exists
    2. Standard layout A/B/C based on page_template
    3. Fall back to C if the specific file is missing or invalid
    """
    # Premium custom path
    if (
        artisan.is_premium
        and artisan.page_template == 'D'
        and artisan.premium_page_published
    ):
        premium_path = f'artisans/premium/{artisan.pk}_premium_page.html'
        try:
            get_template(premium_path)  # Raises TemplateDoesNotExist if missing
            return premium_path
        except TemplateDoesNotExist:
            # Custom file missing — log a warning, fall back to standard
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Premium template missing for CreatorProfile pk={artisan.pk} "
                f"({artisan.display_name}). Falling back to layout C."
            )
            # fall through to standard dispatch

    # Standard layout
    template_map = {
        'A': 'artisans/detail/artisan_detail_a.html',
        'B': 'artisans/detail/artisan_detail_b.html',
        'C': 'artisans/detail/artisan_detail_c.html',
    }
    return template_map.get(
        artisan.page_template,
        'artisans/detail/artisan_detail_c.html'  # safe default
    )


def artisan_detail(request, slug):
    artisan = get_object_or_404(CreatorProfile, slug=slug, is_verified=True)

    all_products = (
        artisan.products
        .filter(is_active=True)
        .select_related('category')
        .order_by('-created_date')
    )
    product_count = all_products.count()
    products = all_products[:PRODUCTS_PREVIEW_LIMIT]

    blog_posts = (
        Post.objects
        .filter(creator=artisan, status='Published')
        .order_by('-created_at')[:3]
    )

    gallery_items = (
        ProductGallery.objects
        .filter(
            product__creator=artisan,
            product__is_active=True,
            is_featured_in_gallery=True,
        )
        .select_related('product')
        .order_by('-gallery_order', '?')[:12]
    )

    other_artisans = (
        CreatorProfile.objects
        .filter(is_verified=True)
        .exclude(pk=artisan.pk)
        .order_by('-is_premium', '-created_at')[:4]
    )

    template_name = resolve_artisan_template(artisan)

    context = {
        'artisan': artisan,
        'products': products,
        'product_count': product_count,
        'has_more_products': product_count > PRODUCTS_PREVIEW_LIMIT,
        'blog_posts': blog_posts,
        'gallery_items': gallery_items,
        'other_artisans': other_artisans,
        'page_title': f'{artisan.display_name}｜匠人',
    }
    return render(request, template_name, context)


def _pick_one_image_per_product(queryset, seed_extra=''):
    """
    Given a queryset of ProductGallery items, returns a Python list with
    ONE item per product (randomly chosen), shuffled deterministically for
    the current day. Rotates at midnight.
    """
    today = timezone.now().strftime('%Y%m%d')
    seed_str = f"{today}:{seed_extra}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    rnd = random.Random(seed)

    # Group items by product
    by_product = {}
    for item in queryset:
        by_product.setdefault(item.product_id, []).append(item)

    # Pick one per product
    chosen = [rnd.choice(items) for items in by_product.values()]

    # Shuffle the final order
    rnd.shuffle(chosen)
    return chosen


def artisan_gallery(request):
    qs = (
        ProductGallery.objects
        .filter(
            is_featured_in_gallery=True,
            product__is_active=True,
            product__creator__isnull=False,
            product__creator__is_verified=True,
        )
        .select_related('product', 'product__creator')
    )

    craft = request.GET.get('craft', '').strip()
    if craft:
        # qs = qs.filter(product__creator__craft_types__name=craft).distinct()
        qs = qs.filter(
            Q(product__craft_types__name=craft) |
            Q(product__craft_types__isnull=True, product__creator__craft_types__name=craft)
        ).distinct()

    # 🌟 One image per product, rotated daily
    images = _pick_one_image_per_product(qs, seed_extra='artisan-gallery')[:60]

    context = {
        'images': images,
        'image_count': len(images),
        'craft_choices': CraftType.objects.all(),
        'current_craft': craft,
        'page_title': 'Gallery｜匠作',
        'main_title': 'Gallery｜匠作',
        'sub_title_1': 'A visual stroll through the artisan market.',
        'sub_title_2': '漫步於匠人的市集之間。',
        'bread_crumb_1': 'Home｜首頁',
        'bread_crumb_2': 'Artisans｜匠人',
        'bread_crumb_3': 'Gallery｜匠作',
        'bread_crumb_1_url': '/',
        'bread_crumb_2_url': '/artisans/',
        'bread_crumb_3_url': '/artisans/gallery/',
    }

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/partials/_gallery_region.html', context)

    return render(request, 'artisans/artisan_gallery.html', context)


def artisan_blog_list(request):
    """
    Hub for browsing all artisan-authored blog posts.
    Search + optional craft filter, chronological feed.
    """

    qs = (
        Post.objects
        .filter(
            status='Published',
            creator__isnull=False,
            creator__is_verified=True,
        )
        .select_related('creator')
        .order_by('-created_at')
    )
    # ── SEARCH ─────────────────────────────────────────
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(short_description__icontains=q) |
            Q(blog_body__icontains=q) |
            Q(creator__display_name__icontains=q) |
            Q(creator__tagline__icontains=q) |
            Q(creator__bio__icontains=q) |
            Q(creator__province__icontains=q) |
            Q(creator__city__icontains=q) |
            Q(creator__craft_types__name__icontains=q) |
            Q(creator__craft_types__label__icontains=q) |
            Q(tags__name__icontains=q)
        ).distinct()

    # ── OPTIONAL CRAFT FILTER ──────────────────────────
    craft = request.GET.get('craft', '').strip()
    if craft:
        qs = qs.filter(creator__craft_types__name=craft).distinct()

    # ── ARTISAN FILTER ──────────────────────────
    artisan_slug = request.GET.get('artisan', '').strip()
    if artisan_slug:
        qs = qs.filter(creator__slug=artisan_slug)

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'posts': page_obj,
        'craft_choices': CraftType.objects.all(),
        'current_q': q,
        'current_craft': craft,
        'page_title': 'Artisan Notes｜匠人筆記',
        'main_title': 'Artisan Notes｜匠人筆記',
        'sub_title_1': 'Stories, reflections, and process notes from the atelier.',
        'sub_title_2': '來自工坊的故事、思緒與創作歷程。',
        'bread_crumb_1': 'Home｜首頁',
        'bread_crumb_2': 'Artisans｜匠人',
        'bread_crumb_3': 'Notes｜筆記',
        'bread_crumb_1_url': '/',
        'bread_crumb_2_url': '/artisans/',
        'bread_crumb_3_url': '/artisans/blogs/',
    }

    # HTMX intercept — return only the grid partial
    if request.headers.get('HX-Request'):
        return render(request, 'artisans/partials/_artisan_notes_region.html', context)
    
    return render(request, 'artisans/artisan_blog_list.html', context)


def artisan_join(request):
    """
    Public join page: pitch + application form.
    Generates a math puzzle and stores the expected answer in the session.
    """
    if request.method == 'POST':
        form = ArtisanApplicationForm(request.POST)
        if form.is_valid():
            # ── Anti-bot checks ──
            # 1. Time check
            timestamp_str = form.cleaned_data.get('render_timestamp', '')
            if timestamp_str:
                try:
                    rendered_at = datetime.fromisoformat(timestamp_str)
                    elapsed = (timezone.now() - rendered_at).total_seconds()
                    if elapsed < 3:
                        form.add_error(None, "Submission too fast. Please try again.")
                        return _render_join_with_new_math(request, form)
                except (ValueError, TypeError):
                    pass

            # 2. Math check
            expected = request.session.get('join_math_answer')
            given = form.cleaned_data.get('math_answer')
            if expected is None or str(given) != str(expected):
                form.add_error('math_answer', "走神了？再算一遍～")
                return _render_join_with_new_math(request, form)

            # 3. Store the cleaned data in session and redirect to a PDF-gen endpoint
            request.session['pending_application'] = {
                'display_name': form.cleaned_data['display_name'],
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data.get('phone', ''),
                'wechat': form.cleaned_data.get('wechat', ''),
                'province': form.cleaned_data['province'],
                'city': form.cleaned_data.get('city', ''),
                'craft_types': [ct.label for ct in form.cleaned_data['craft_types']],
                'portfolio_url': form.cleaned_data.get('portfolio_url', ''),
                'short_bio': form.cleaned_data['short_bio'],
                'reason_for_joining': form.cleaned_data['reason_for_joining'],
                'submitted_at': timezone.now().strftime('%Y-%m-%d %H:%M'),
            }
            request.session.modified = True
            return redirect('artisan_join_success')

        # Invalid — regenerate math and re-render
        return _render_join_with_new_math(request, form)

    # GET — render fresh form with new math
    form = ArtisanApplicationForm()
    return _render_join_with_new_math(request, form)


def _render_join_with_new_math(request, form):
    """Helper: generates a new math challenge, stores answer in session, renders the page."""
    a = random.randint(3, 12)
    b = random.randint(2, 9)
    request.session['join_math_answer'] = str(a + b)
    request.session['join_math_prompt'] = f"What is {a} + {b}?"
    request.session.modified = True

    context = {
        'form': form,
        'math_prompt': request.session['join_math_prompt'],
        'page_title': 'Join as Artisan｜同匠',
        'main_title': 'Become an Artisan｜成為匠人',
        'sub_title_1': 'If your hands shape things with care, we would love to hear from you.',
        'sub_title_2': '若您以匠心親手造物，我們誠摯期待您的加入。',
    }
    return render(request, 'artisans/artisan_join.html', context)


def artisan_join_success(request):
    pending = request.session.get('pending_application')
    if not pending:
        return redirect('artisan_join')

    recipient_email = 'hello@yourdomain.com'   # ← REPLACE with your real address
    subject = f"匠人申請 — {pending['display_name']}"

    plain_body = (
        f"您好，\n\n"
        f"我是 {pending['display_name']}（{pending['full_name']}），"
        f"來自 {pending['province']}"
        f"{' ' + pending['city'] if pending.get('city') else ''}，"
        f"專注於 {', '.join(pending['craft_types'])}。\n\n"
        f"我的申請文件已附於此郵件。\n\n"
        f"聯絡方式：\n"
        f"電郵：{pending['email']}\n"
    )
    if pending.get('phone'):
        plain_body += f"電話：{pending['phone']}\n"
    if pending.get('wechat'):
        plain_body += f"微信：{pending['wechat']}\n"
    plain_body += "\n謝謝！\n"

    from urllib.parse import quote
    mailto_url = f"mailto:{recipient_email}?subject={quote(subject)}&body={quote(plain_body)}"

    context = {
        'pending': pending,
        'mailto_url': mailto_url,
        'recipient_email': recipient_email,
        'subject': subject,
        'plain_body': plain_body,
        'page_title': 'Application Ready｜申請已備妥',
    }
    return render(request, 'artisans/artisan_join_success.html', context)


def artisan_join_pdf(request):
    """
    Generate the application PDF from the session-stored data and serve as a download.
    """
    pending = request.session.get('pending_application')
    if not pending:
        return redirect('artisan_join')

    from .utils import generate_application_pdf
    pdf_buffer = generate_application_pdf(pending)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"application_{pending['display_name']}.pdf",
        content_type='application/pdf',
    )


# ═══════════════════════════════════════════════════════════════════════════
# ROLE SWITCH — Dual-role login flow
# ═══════════════════════════════════════════════════════════════════════════

@login_required
def role_select(request):
    """
    If a verified artisan logs in, this page asks: 'Buyer or Creator?'
    Non-artisans get silently redirected to the standard dashboard.
    """
    profile = getattr(request.user, 'creator_profile', None)
    if not profile or not profile.is_verified:
        return redirect('dashboard')  # your existing member dashboard URL name
    return render(request, 'artisans/role_select.html', {
        'profile': profile,
        'page_title': 'Choose View｜選擇模式',
    })


@login_required
def set_role(request, role):
    """
    Session-based role switch. Sets active_role then redirects to correct dashboard.
    """
    if role not in ('buyer', 'creator'):
        return redirect('home')

    if role == 'creator':
        profile = getattr(request.user, 'creator_profile', None)
        if not profile or not profile.is_verified:
            return redirect('dashboard', subpage="main")
        request.session['active_role'] = 'creator'
        return redirect('a_dashboard')

    request.session['active_role'] = 'buyer'
    return redirect('dashboard', subpage="main")  # your member dashboard URL name


# ═══════════════════════════════════════════════════════════════════════════
# ARTISAN DASHBOARD — 匠人工作台
# ═══════════════════════════════════════════════════════════════════════════

@artisan_required
def dashboard_overview(request):
    profile = request.user.creator_profile

    pending_lines = OrderProduct.objects.filter(
        fulfilled_by=profile,
        is_dispatched=False,
    ).select_related('order', 'product', 'product_variation').order_by('-order__created_at')

    dispatched_this_week = OrderProduct.objects.filter(
        fulfilled_by=profile,
        is_dispatched=True,
        dispatched_at__gte=timezone.now() - timedelta(days=7),
    ).count()

    total_products = profile.products.filter(is_active=True).count()
    recent_posts = profile.posts.filter(status='Published').order_by('-created_at')[:3]

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'overview',
        'dispatched_this_week': dispatched_this_week,
        'total_products': total_products,
        'pending_lines_preview': pending_lines[:5],
        'recent_posts': recent_posts,
        'page_title': 'Overview｜匠人工作台',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_overview_panel.html', context)
    return render(request, 'artisans/dashboard/overview.html', context)


@artisan_required
def dashboard_orders(request):
    profile = request.user.creator_profile

    base_qs = OrderProduct.objects.filter(
        fulfilled_by=profile,
    ).select_related(
        'order', 'product', 'product_variation',
    ).prefetch_related(
        Prefetch('tracking_assignments', queryset=TrackingNumber.objects.all())
    ).order_by('-order__created_at')

    # Pending lines are bucketed by product type. The artisan has a
    # distinct action (or no action) per bucket:
    #
    #   pending_physical        — enter a tracking number to dispatch
    #   pending_custom_digital  — produce and upload the file for
    #                             admin review (via the product edit
    #                             page's vault-upload modal)
    #
    # INSTANT digital and voucher lines auto-fulfil at payment time and
    # are deliberately excluded. They stay in the queryset only if a
    # historical row predates the auto-fulfil flip; excluding them
    # here means a stale line can't block the artisan's view.
    pending_qs = base_qs.filter(is_dispatched=False)
    pending_physical = pending_qs.filter(product__is_physical=True)
    pending_custom_digital = pending_qs.filter(
        product__is_digital=True,
        product__digital_fulfillment_type="CUSTOM",
    )

    dispatched_lines = base_qs.filter(is_dispatched=True).exclude(order__order_status='Delivered')[:20]
    delivered_lines = (
        base_qs
        .filter(order__order_status='Delivered')
        .order_by('-dispatched_at', '-order__updated_at')[:20]
    )
    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'orders',
        'pending_physical': pending_physical,
        'pending_custom_digital': pending_custom_digital,
        'dispatched_lines': dispatched_lines,
        'delivered_lines': delivered_lines,
        'page_title': 'Orders｜訂單',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_orders_panel.html', context)
    return render(request, 'artisans/dashboard/orders.html', context)


@artisan_required
@require_POST
def dashboard_dispatch_line(request, line_id):
    profile = request.user.creator_profile
    line = get_object_or_404(
        OrderProduct, id=line_id, fulfilled_by=profile, is_dispatched=False,
    )

    if not line.product.is_physical:
        messages.error(
            request,
            "Only physical items can be dispatched.｜只有實體商品可標記發貨。",
        )
        return dashboard_orders(request)

    tracking_code = request.POST.get('tracking_code', '').strip()
    carrier = request.POST.get('carrier', '').strip()

    if not tracking_code:
        messages.error(request, "Tracking number is required.｜請填寫物流單號。")
        return dashboard_orders(request)

    with transaction.atomic():
        line.is_dispatched = True
        line.dispatched_at = timezone.now()
        line.save(update_fields=['is_dispatched', 'dispatched_at'])

        TrackingNumber.objects.create(
            order=line.order,
            order_product=line,
            tracking_code=tracking_code,
            carrier_name=carrier,
        )

    messages.success(request, "Line dispatched successfully.｜已標記發貨。")
    return dashboard_orders(request)


@artisan_required
def dashboard_blog_list(request):
    """List all of this artisan's own blog posts."""
    profile = request.user.creator_profile

    posts = (
        Post.objects
        .filter(creator=profile, is_deleted=False)
        .order_by('-updated_at')
    )

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'blog',
        'posts': posts,
        'page_title': 'Blog｜筆記',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_blog_panel.html', context)
    return render(request, 'artisans/dashboard/blog.html', context)


@artisan_required
def dashboard_blog_create(request):
    profile = request.user.creator_profile

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                post = form.save(commit=False)
                post.author = request.user
                post.creator = profile
                post.post_type = 'Blog'
                post.save()
                form.save_m2m()

                duplicate_count = Post.objects.filter(
                    creator=profile,
                    title__iexact=post.title,
                    is_deleted=False,
                ).exclude(pk=post.pk).count()

            messages.success(request, "草稿已儲存。｜Draft saved.")
            if duplicate_count:
                messages.info(
                    request,
                    f"注意：您已有 {duplicate_count} 篇相同標題的筆記（不影響儲存）。"
                    f"｜Note: You already have {duplicate_count} post(s) with the same title (saved anyway)."
                )
            return redirect('a_dashboard_blog')
    else:
        form = BlogPostForm()

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'blog',
        'form': form,
        'is_editing': False,
        'page_title': 'New Post｜新筆記',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_blog_editor_panel.html', context)
    return render(request, 'artisans/dashboard/blog_editor.html', context)


@artisan_required
def dashboard_blog_edit(request, pk):
    """Edit a draft or rejected post. Published/Pending posts are locked."""
    profile = request.user.creator_profile
    post = get_object_or_404(Post, pk=pk, creator=profile)

    if post.status not in ('Draft', 'Rejected'):
        messages.warning(
            request,
            "只有草稿或未通過的筆記可以編輯。｜Only drafts and rejected posts can be edited."
        )
        return redirect('a_dashboard_blog')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            with transaction.atomic():
                post = form.save()

                duplicate_count = Post.objects.filter(
                    creator=profile,
                    title__iexact=post.title,
                    is_deleted=False,
                ).exclude(pk=post.pk).count()

            messages.success(request, "筆記已更新。｜Post updated.")
            if duplicate_count:
                messages.info(
                    request,
                    f"注意：您已有 {duplicate_count} 篇相同標題的筆記（不影響儲存）。"
                    f"｜Note: You already have {duplicate_count} post(s) with the same title (saved anyway)."
                )
            return redirect('a_dashboard_blog')
    else:
        form = BlogPostForm(instance=post)

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'blog',
        'form': form,
        'post': post,
        'is_editing': True,
        'page_title': f'Edit: {post.title}｜編輯筆記',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_blog_editor_panel.html', context)
    return render(request, 'artisans/dashboard/blog_editor.html', context)


@artisan_required
@require_POST
def dashboard_blog_submit(request, pk):
    """Submit a draft or rejected post for review."""
    profile = request.user.creator_profile
    post = get_object_or_404(Post, pk=pk, creator=profile)

    if post.status not in ('Draft', 'Rejected'):
        messages.error(request, "此筆記目前無法提交審核。｜This post cannot be submitted now.")
        return redirect('a_dashboard_blog')

    # ── A2: submission-time image requirement ──
    if not post.featured_image:
        messages.error(
            request,
            "提交審核前請先上傳封面圖。"
            "｜Featured image is required before submitting for review."
        )
        return redirect('a_dashboard_blog')

    with transaction.atomic():
        post.status = 'Pending'
        post.save(update_fields=['status'])

        BlogPostReviewLog.objects.create(
            post=post,
            action='submitted',
            actor=request.user,
            note='Author submitted for review.',
        )

    # 🌟 Notification email hook (added in Phase C)
    transaction.on_commit(lambda: send_blog_submission_email_task.delay(post.id))

    messages.success(
        request,
        "已提交審核。管理員會盡快查看。｜Submitted for review."
    )
    return redirect('a_dashboard_blog')


@artisan_required
@require_POST
def dashboard_blog_withdraw(request, pk):
    """Withdraw a post from the review queue and revert to Draft."""
    profile = request.user.creator_profile
    post = get_object_or_404(Post, pk=pk, creator=profile)

    if post.status != 'Pending':
        messages.error(request, "只有待審核的筆記可以撤回。｜Only pending posts can be withdrawn.")
        return redirect('a_dashboard_blog')

    with transaction.atomic():
        post.status = 'Draft'
        post.save(update_fields=['status'])

        BlogPostReviewLog.objects.create(
            post=post,
            action='withdrawn',
            actor=request.user,
            note='Author withdrew the submission.',
        )

    messages.success(request, "已撤回審核。｜Submission withdrawn.")
    return redirect('a_dashboard_blog')


@artisan_required
@require_POST
def dashboard_blog_delete(request, pk):
    """Soft-delete a draft/rejected/unpublished post."""
    profile = request.user.creator_profile
    post = get_object_or_404(Post, pk=pk, creator=profile, is_deleted=False)

    if not post.can_be_deleted_by_artisan:
        messages.error(
            request,
            "只有草稿、未通過或已下架的筆記可以刪除。"
            "｜Only drafts, rejected, or unpublished posts can be deleted."
        )
        return redirect('a_dashboard_blog')

    previous_status = post.status
    title = post.title

    with transaction.atomic():
        post.is_deleted = True
        post.save(update_fields=["is_deleted"])

        BlogPostReviewLog.objects.create(
            post=post,
            action="deleted_by_author",
            actor=request.user,
            note=f"Author soft-deleted post (previous status: {previous_status}).",
        )

    messages.success(request, f"已刪除：{title}｜Deleted.")
    return redirect('a_dashboard_blog')


@artisan_required
@require_POST
def dashboard_blog_bulk_delete_drafts(request):
    """Soft-delete all of this artisan's Draft posts at once."""
    profile = request.user.creator_profile
    drafts = Post.objects.filter(creator=profile, status="Draft", is_deleted=False)

    count = drafts.count()
    if count == 0:
        messages.info(request, "沒有草稿可清除。｜No drafts to clear.")
        return redirect('a_dashboard_blog')

    with transaction.atomic():
        for post in drafts:
            post.is_deleted = True
            post.save(update_fields=["is_deleted"])
            BlogPostReviewLog.objects.create(
                post=post,
                action="deleted_by_author",
                actor=request.user,
                note="Author bulk-cleared drafts.",
            )

    messages.success(request, f"已清除 {count} 篇草稿。｜Cleared {count} draft(s).")
    return redirect('a_dashboard_blog')


@artisan_required
def dashboard_profile_edit(request):
    profile = request.user.creator_profile

    if request.method == 'POST':
        form = CreatorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "您的匠人檔案已更新。｜Profile updated successfully.")

            # Redirect to refresh the view (avoids re-POST on refresh)
            url = reverse('a_dashboard_profile')
            if request.headers.get('HX-Request'):
                response = HttpResponse("", status=200)
                response['HX-Redirect'] = url
                return response
            return redirect('a_dashboard_profile')
    else:
        form = CreatorProfileForm(instance=profile)

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'profile',
        'form': form,
        'page_title': 'Profile｜匠人檔案',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_profile_panel.html', context)
    return render(request, 'artisans/dashboard/profile.html', context)


@artisan_required
def dashboard_messages(request):
    """
    Artisan inbox: thread list plus, when ?customer=<id> is present,
    the active thread's messages.

    Opening a thread flips every unread customer-authored message in
    that thread to read. Artisan-authored messages are already
    is_read=True and are unaffected.
    """
    profile = request.user.creator_profile
    customer_id = request.GET.get("customer")

    # One row per customer who has exchanged messages with this artisan.
    # last_at is used to order threads most-recently-active first.
    thread_rows = list(
        ArtisanChatMessage.objects
        .filter(artisan=profile)
        .values("customer")
        .annotate(last_at=Max("created_at"), unread=Count("id", filter=Q(is_read=False)))
        .order_by("-last_at")
    )

    # Fetch the customer Accounts in one query rather than N.
    customer_ids = [row["customer"] for row in thread_rows]
    customers_by_id = {
        u.id: u for u in Account.objects.filter(id__in=customer_ids)
    }
    for row in thread_rows:
        row["customer_obj"] = customers_by_id.get(row["customer"])

    active_customer = None
    active_messages = ArtisanChatMessage.objects.none()

    if customer_id:
        active_customer = customers_by_id.get(int(customer_id)) if customer_id.isdigit() else None
        if active_customer is None:
            # The customer isn't in this artisan's existing threads.
            # Load them anyway if they exist as an Account — a fresh
            # thread starts empty.
            active_customer = Account.objects.filter(id=customer_id).first()
        if active_customer:
            active_messages = (
                ArtisanChatMessage.objects
                .filter(artisan=profile, customer=active_customer)
                .select_related("sender")
            )
            ArtisanChatMessage.objects.filter(
                artisan=profile,
                customer=active_customer,
                is_read=False,
            ).update(is_read=True)

    context = artisan_dashboard_context(request)
    context.update({
        "active_section": "messages",
        "threads": thread_rows,
        "active_customer": active_customer,
        "active_messages": active_messages,
        "page_title": "Messages｜訊息",
    })

    if request.headers.get("HX-Request"):
        return render(request, "artisans/dashboard/partials/_messages_panel.html", context)
    return render(request, "artisans/dashboard/messages.html", context)


@artisan_required
@require_POST
def dashboard_messages_send(request, customer_id):
    """
    Create a message from this artisan to the given customer.

    Redirects back to the thread. No WebSocket — the reload is what
    delivers the update.
    """
    profile = request.user.creator_profile
    customer = get_object_or_404(Account, pk=customer_id)

    content = (request.POST.get("content") or "").strip()
    if not content:
        messages.error(request, "Message cannot be empty.｜訊息不得為空。")
        return redirect(f"{reverse('a_dashboard_messages')}?customer={customer.id}")

    ArtisanChatMessage.objects.create(
        artisan=profile,
        customer=customer,
        sender=request.user,
        content=content,
        is_read=True,
    )
    return redirect(f"{reverse('a_dashboard_messages')}?customer={customer.id}")


# Product Registration
@artisan_required
def dashboard_products_list(request):
    """List this artisan's products, all statuses."""
    profile = request.user.creator_profile
    products = (
        Product.objects
        .filter(creator=profile, is_deleted=False)
        .order_by('-modified_date')
    )

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'products',
        'products': products,
        'page_title': 'Products｜作品',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_products_panel.html', context)
    return render(request, 'artisans/dashboard/products.html', context)


@artisan_required
def dashboard_product_create(request):
    """
    Phase 1: create the product shell with metadata.
    Variations are added afterwards (on the edit page).
    """
    profile = request.user.creator_profile

    if request.method == 'POST':
        form = ArtisanProductForm(request.POST, request.FILES, artisan=profile)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save()
                    # Product-level gallery images
                    for f in request.FILES.getlist('gallery_images'):
                        ProductGallery.objects.create(product=product, image=f)
            except IntegrityError as e:
                msg = str(e)
                if 'product_name' in msg:
                    form.add_error(
                        'product_name',
                        "此作品名稱已被使用。｜This product name is already in use."
                    )
                elif 'slug' in msg:
                    form.add_error(
                        None,
                        "網址代稱衝突，請稍後再試。｜URL slug conflict. Please try again."
                    )
                else:
                    raise  # Unknown integrity error — re-raise
            else:
                messages.success(
                    request,
                    "作品已建立為草稿。現在可以新增款式。｜Product created as draft. Now add variations."
                )
                return redirect('a_dashboard_product_edit', pk=product.pk)
    else:
        form = ArtisanProductForm(artisan=profile)

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'products',
        'form': form,
        'is_editing': False,
        'page_title': 'New Product｜新作品',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_product_editor_panel.html', context)
    return render(request, 'artisans/dashboard/product_editor.html', context)


@artisan_required
def dashboard_product_edit(request, pk):
    """
    Phase 2: edit metadata + manage variations via dedicated endpoints.
    """
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if not product.is_editable_by_artisan:
        messages.warning(
            request,
            "只有草稿、未通過或已下架的作品可以編輯。｜Only drafts, rejected, or unpublished products can be edited."
        )
        return redirect('a_dashboard_products')

    if request.method == 'POST':
        is_submitting = request.POST.get('action') == 'save_and_submit'

        form = ArtisanProductForm(
            request.POST, request.FILES, 
            instance=product, artisan=profile,
            require_image=is_submitting,
        )
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    for f in request.FILES.getlist('gallery_images'):
                        ProductGallery.objects.create(product=product, image=f)
            except IntegrityError as e:
                msg = str(e)
                if 'product_name' in msg:
                    form.add_error(
                        'product_name',
                        "此作品名稱已被使用。｜This product name is already in use."
                    )
                elif 'slug' in msg:
                    form.add_error(
                        None,
                        "網址代稱衝突，請稍後再試。｜URL slug conflict. Please try again."
                    )
                else:
                    raise
            else:
                if is_submitting:
                    if not product.variations.exists():
                        messages.error(
                            request,
                            "提交前請至少新增一個款式。｜Add at least one variation before submitting."
                        )
                    else:
                        with transaction.atomic():
                            product.status = 'Pending'
                            product.submitted_at = timezone.now()
                            product.save(update_fields=['status', 'submitted_at'])

                            ProductReviewLog.objects.create(
                                product=product,
                                action='submitted',
                                actor=request.user,
                                note='Author submitted for review.',
                            )

                        transaction.on_commit(
                            lambda: send_product_submission_email_task.delay(product.id)
                        )

                        messages.success(request, "已提交審核。｜Submitted for review.")
                        return redirect('a_dashboard_products')

                else:
                    # Plain "Save Draft" — stay on the edit page
                    messages.success(request, "作品已更新。｜Product updated.")
                    return redirect('a_dashboard_product_edit', pk=product.pk)
    else:
        form = ArtisanProductForm(instance=product, artisan=profile)

    variations = product.variations.all().order_by('created_date')
    gallery_images = product.productgallery_set.all()

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'products',
        'form': form,
        'product': product,
        'variations': variations,
        'gallery_images': gallery_images,
        'is_editing': True,
        'page_title': f'Edit: {product.product_name}｜編輯作品',
        'variation_form': ProductVariationForm(),
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_product_editor_panel.html', context)
    return render(request, 'artisans/dashboard/product_editor.html', context)


@artisan_required
@require_POST
def dashboard_product_variation_add(request, pk):
    """Add a variation to a draft/rejected/unpublished product."""
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if not product.is_editable_by_artisan:
        return JsonResponse(
            {'error': '此作品目前無法編輯。｜Product cannot be edited now.'},
            status=403,
        )

    form = ProductVariationForm(request.POST, request.FILES)
    if not form.is_valid():
        # Return errors as JSON for the modal to display
        return JsonResponse({'errors': form.errors}, status=400)

    try:
        with transaction.atomic():
            variation = form.save(commit=False)
            variation.product = product
            variation.save()
    except IntegrityError:
        return JsonResponse(
            {'error': '此款式組合已存在，請勿重複。｜A variation with this combination already exists.'},
            status=400,
        )

    # Return the refreshed cards partial
    variations = product.variations.all().order_by('created_date')
    return render(request, 'artisans/dashboard/partials/_product_variation_cards.html', {
        'product': product,
        'variations': variations,
    })


@artisan_required
@require_POST
def dashboard_product_variation_remove(request, pk, variation_pk):
    """Delete a variation from a draft/rejected/unpublished product."""
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if not product.is_editable_by_artisan:
        return JsonResponse(
            {'error': '此作品目前無法編輯。｜Product cannot be edited now.'},
            status=403,
        )

    variation = get_object_or_404(ProductVariation, pk=variation_pk, product=product)
    variation.delete()

    variations = product.variations.all().order_by('created_date')
    return render(request, 'artisans/dashboard/partials/_product_variation_cards.html', {
        'product': product,
        'variations': variations,
    })


@artisan_required
@require_POST
def dashboard_product_gallery_delete(request, pk, gallery_pk):
    """Delete a single ProductGallery image from a draft/rejected/unpublished product."""
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if not product.is_editable_by_artisan:
        return JsonResponse(
            {'error': '此作品目前無法編輯。｜Product cannot be edited now.'},
            status=403,
        )

    gallery_image = get_object_or_404(
        ProductGallery, pk=gallery_pk, product=product,
    )

    # ── Delete the DB row. The file_cleanup post_delete hook
    #    removes the file from storage (see note below).
    gallery_image.delete()

    # Return the refreshed gallery grid (HTMX swaps it in place).
    gallery_images = product.productgallery_set.all()
    return render(request, 'artisans/dashboard/partials/_product_gallery_grid.html', {
        'product': product,
        'gallery_images': gallery_images,
    })


@artisan_required
@require_POST
def dashboard_product_submit(request, pk):
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if not product.is_editable_by_artisan:
        messages.error(request, "此作品目前無法提交審核。")
        return redirect('a_dashboard_products')

    # ── A2: submission-time image requirement ──
    if not product.images:
        messages.error(
            request,
            "提交審核前請先上傳作品主視覺。"
            "｜Featured image is required before submitting for review."
        )
        return redirect('a_dashboard_products')

    if not product.variations.exists():
        messages.error(
            request,
            "提交前請至少新增一個款式。｜Add at least one variation before submitting."
        )
        return redirect('a_dashboard_products')

    with transaction.atomic():
        product.status = 'Pending'
        product.submitted_at = timezone.now()
        product.save(update_fields=['status', 'submitted_at'])

        ProductReviewLog.objects.create(
            product=product,
            action='submitted',
            actor=request.user,
            note='Author submitted for review.',
        )

    transaction.on_commit(
        lambda: send_product_submission_email_task.delay(product.id)
    )

    messages.success(request, "已提交審核。｜Submitted for review.")
    return redirect('a_dashboard_products')


@artisan_required
@require_POST
def dashboard_product_withdraw(request, pk):
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if product.status != 'Pending':
        messages.error(request, "只有待審核的作品可以撤回。")
        return redirect('a_dashboard_products')

    with transaction.atomic():
        product.status = 'Draft'
        product.save(update_fields=['status'])

        ProductReviewLog.objects.create(
            product=product,
            action='withdrawn',
            actor=request.user,
            note='Author withdrew the submission.',
        )

    messages.success(request, "已撤回審核。｜Submission withdrawn.")
    return redirect('a_dashboard_products')


@artisan_required
@require_POST
def dashboard_product_variation_edit(request, pk, variation_pk):
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if not product.is_editable_by_artisan:
        return JsonResponse(
            {'error': '此作品目前無法編輯。｜Product cannot be edited now.'},
            status=403,
        )

    variation = get_object_or_404(ProductVariation, pk=variation_pk, product=product)
    form = ProductVariationForm(request.POST, request.FILES, instance=variation)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    try:
        with transaction.atomic():
            form.save()
    except IntegrityError:
        return JsonResponse(
            {'error': '此款式組合已存在，請勿重複。｜A variation with this combination already exists.'},
            status=400,
        )

    variations = product.variations.all().order_by('created_date')
    return render(request, 'artisans/dashboard/partials/_product_variation_cards.html', {
        'product': product,
        'variations': variations,
    })


@artisan_required
@require_POST
def dashboard_product_delete(request, pk):
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if product.status not in ("Draft", "Rejected", "Unpublished"):
        messages.error(request, "只有草稿、未通過或已下架的作品可以刪除。")
        return redirect("a_dashboard_products")

    previous_status = product.status
    title = product.product_name

    with transaction.atomic():
        product.is_deleted = True
        product.is_active = False
        product.save(update_fields=["is_deleted", "is_active"])

        ProductReviewLog.objects.create(
            product=product,
            action="deleted_by_author",
            actor=request.user,
            note=f"Author soft-deleted product (previous status: {previous_status}).",
        )

    messages.success(request, f"已刪除：{title}｜Deleted.")
    return redirect("a_dashboard_products")


@artisan_required
def dashboard_product_stock_edit(request, pk):
    """Renders the stock-edit modal, or saves on POST."""
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if product.status != "Published":
        messages.error(request, "只有已發布的作品可以調整庫存。｜Only published products can have their stock adjusted.")
        return redirect("a_dashboard_products")

    variations = product.variations.all().order_by("created_date")

    if request.method == "POST":
        updated = 0
        for v in variations:
            field_name = f"stock_{v.id}"
            if field_name in request.POST:
                try:
                    new_stock = int(request.POST[field_name])
                except (ValueError, TypeError):
                    continue
                if new_stock < 0:
                    new_stock = 0
                if new_stock != v.stock:
                    v.stock = new_stock
                    # Respect the instant-digital rule: force stock=1
                    if v.product.is_digital and v.product.digital_fulfillment_type == "INSTANT" and not v.product.is_voucher:
                        v.stock = 1
                    v.save(update_fields=["stock"])
                    updated += 1

        messages.success(request, f"已更新 {updated} 個款式的庫存。｜Updated stock for {updated} variation(s).")
        return redirect("a_dashboard_products")

    # GET: render the modal content (returns a partial for the modal)
    context = {
        "product": product,
        "variations": variations,
    }
    return render(request, "artisans/dashboard/partials/_product_stock_modal.html", context)


@artisan_required
@require_POST
def dashboard_product_request_deactivation(request, pk):
    profile = request.user.creator_profile
    product = get_object_or_404(Product, pk=pk, creator=profile, is_deleted=False)

    if product.status != "Published":
        messages.error(request, "只有已發布的作品可以申請下架。")
        return redirect("a_dashboard_products")

    reason = request.POST.get("reason", "").strip()
    if not reason:
        messages.error(request, "請說明下架原因。｜Please provide a reason.")
        return redirect("a_dashboard_products")

    # Actually — we want to allow re-requesting after a rejection, so we'd check
    # whether the most recent log entry is an outstanding request.
    latest = product.review_logs.order_by("-created_at").first()
    if latest and latest.action == "deactivation_requested":
        messages.info(request, "您已提交下架請求，管理員將盡快處理。｜Request already pending.")
        return redirect("a_dashboard_products")

    with transaction.atomic():
        ProductReviewLog.objects.create(
            product=product,
            action="deactivation_requested",
            actor=request.user,
            note=reason,
        )

        transaction.on_commit(
            lambda: send_product_deactivation_request_email_task.delay(product.id)
        )

    messages.success(request, "已提交下架請求，管理員將盡快處理。｜Deactivation request submitted.")
    return redirect("a_dashboard_products")


# ═══════════════════════════════════════════════════════════════════════════
# VAULT UPLOAD — artisan staging flow
# ═══════════════════════════════════════════════════════════════════════════

@artisan_required
def dashboard_product_variation_upload_vault(request, pk, variation_pk):
    """
    GET:  return the vault-upload modal body with a fresh form, for HTMX
          to swap into #vault-upload-modal-body.
    POST: validate + stage the submission, then return the refreshed
          variation-cards partial with HX-Retarget so the modal closes
          naturally with the swap.

    Only applies to digital products. Non-digital products 404 — the
    UI hides the button, and the check here closes the forged-POST
    path.
    """
    profile = request.user.creator_profile

    product = get_object_or_404(
        Product,
        pk=pk,
        creator=profile,
        is_deleted=False,
        is_digital=True,
    )
    variation = get_object_or_404(
        ProductVariation, pk=variation_pk, product=product,
    )

    cards_template = "artisans/dashboard/partials/_product_variation_cards.html"
    form_template = "artisans/dashboard/partials/_vault_upload_form.html"

    # ── POST: process the submission ──────────────────────────────
    if request.method == "POST":
        form = ArtisanVaultUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                self_supersede_and_create(
                    profile=profile,
                    product=product,
                    variation=variation,
                    form=form,
                )
            except IntegrityError:
                # Race with a concurrent upload for the same variation
                # from another tab. The partial unique constraint is the
                # guard; the correct recovery is to retry the supersession
                # once (the second call's select_for_update will see the
                # committed PENDING row and flip it to SUPERSEDED before
                # creating the new one). If the retry also fails
                # (three-way race, e.g. a third tab), the exception
                # propagates and the view returns 500 — acceptable
                # for a behaviour this rare; the constraint has still
                # protected the data.
                self_supersede_and_create(
                    profile=profile,
                    product=product,
                    variation=variation,
                    form=form,
                )
            # ── Notify admin after the transaction commits ────────
            # Fetch the newly created PENDING row to get its id for
            # the notification. This is safe immediately after the
            # helper returns — no other writer can create a second
            # PENDING for this variation (partial unique constraint),
            # so `.get()` cannot race here.
            new_upload = ArtisanVaultUpload.objects.get(
                variation=variation, status="PENDING",
            )
            transaction.on_commit(
                lambda uid=new_upload.id:
                    send_vault_upload_pending_email_task.delay(str(uid))
            )
            messages.success(
                request,
                "已提交，等待管理員審核。｜Submitted for admin review.",
            )
            variations = product.variations.all().order_by("created_date")
            response = render(request, cards_template, {
                "product": product,
                "variations": variations,
            })
            response["HX-Retarget"] = "#variation-cards-container"
            return response

        # Invalid: re-render the modal body with errors visible.
        return render(request, form_template, {
            "form": form,
            "product": product,
            "variation": variation,
            "upload_post_url": reverse(
                "a_dashboard_product_variation_upload_vault",
                args=[product.id, variation.id],
            ),
        })

    # ── GET: render empty form for the modal body ─────────────────
    form = ArtisanVaultUploadForm()
    return render(request, form_template, {
        "form": form,
        "product": product,
        "variation": variation,
        "upload_post_url": reverse(
            "a_dashboard_product_variation_upload_vault",
            args=[product.id, variation.id],
        ),
    })


def self_supersede_and_create(*, profile, product, variation, form, order_product=None):
    """
    Small helper: supersede any existing PENDING upload for this target
    (deleting its staged file if one exists), then create the new
    ArtisanVaultUpload row.

    Both actions inside a single transaction so a failure leaves no
    half-superseded state. Filesystem deletions are done in-line and
    are already idempotent (missing_ok=True); a failure there is
    logged but does not roll back the DB — a stray file in _pending/
    is harmless and will be caught by the sweeper command when it
    lands.

    Supersession target: when order_product is set, the supersession
    filter is order_product=order_product; otherwise it is
    variation=variation (the original INSTANT-path behaviour). The
    branch is required because a single variation can host multiple
    CUSTOM order lines, each with its own order-product-scoped PENDING
    upload (per the unique_pending_upload_per_order_product constraint).
    Filtering by variation on the CUSTOM path would supersede the
    wrong line's upload — a silent data bug, not an error. See the
    CUSTOM pipeline v2 handoff.
    """
    pending_root = Path(settings.XINDENG_VAULT_ROOT) / "_pending"

    with transaction.atomic():
        supersede_qs = ArtisanVaultUpload.objects.select_for_update()
        if order_product is not None:
            supersede_qs = supersede_qs.filter(
                order_product=order_product, status="PENDING",
            )
        else:
            supersede_qs = supersede_qs.filter(
                variation=variation, status="PENDING",
            )
        existing = supersede_qs.first()

        if existing is not None:
            if existing.staged_filename:
                old_path = pending_root / existing.staged_filename
                try:
                    old_path.unlink(missing_ok=True)
                except OSError as exc:
                    logger.warning(
                        "Could not delete superseded staged file %s: %s",
                        old_path, exc,
                    )
            existing.status = "SUPERSEDED"
            existing.review_note = "Superseded by a newer upload from the artisan."
            existing.reviewed_at = timezone.now()
            existing.save(update_fields=["status", "review_note", "reviewed_at"])

        upload_type = form.cleaned_data["upload_type"]

        # Shared kwargs for both create branches. order_product is
        # None for the INSTANT path and a real FK for the CUSTOM path;
        # passing None to a nullable FK is a no-op on the row.
        common_kwargs = {
            "artisan": profile,
            "product": product,
            "variation": variation,
            "order_product": order_product,
            "status": "PENDING",
        }

        if upload_type == "DIRECT":
            uploaded = form.cleaned_data["file"]
            original_name = uploaded.name or "upload"
            ext = original_name.rsplit(".", 1)[-1].lower()

            staged_name = f"{uuid.uuid4()}.{ext}"
            pending_root.mkdir(parents=True, exist_ok=True)
            dest_path = pending_root / staged_name

            hasher = hashlib.sha256()
            final_size = 0
            with open(dest_path, "wb") as dest:
                for chunk in uploaded.chunks():
                    hasher.update(chunk)
                    dest.write(chunk)
                    final_size += len(chunk)

            ArtisanVaultUpload.objects.create(
                **common_kwargs,
                storage_kind="LOCAL",
                staged_filename=staged_name,
                original_filename=original_name,
                file_size=final_size,
                checksum=hasher.hexdigest(),
            )
        else:  # EXTERNAL
            ArtisanVaultUpload.objects.create(
                **common_kwargs,
                storage_kind="EXTERNAL_PENDING",
                staged_filename="",
                original_filename="",
                file_size=0,
                checksum=(form.cleaned_data.get("checksum") or "").strip(),
                external_url=form.cleaned_data["external_url"],
            )


@artisan_required
def dashboard_order_product_upload_vault(request, order_product_id):
    """
    GET:  return the vault-upload modal body with a fresh form, for HTMX
          to swap into the artisan orders dashboard's shared modal.
    POST: validate + stage the submission with order_product set, then
          return the refreshed pending-custom-digital partial with
          HX-Retarget so the modal closes naturally with the swap.

    This is the order-product-scoped sibling of
    dashboard_product_variation_upload_vault. The difference is the
    target: this view stages a file against a specific CUSTOM order
    line (OrderProduct), not against a ProductVariation. The distinction
    is load-bearing for the CUSTOM pipeline: the approve view branches
    on upload.order_product_id to decide whether to write
    OrderProduct.digital_file_path (this path) or
    ProductVariation.digital_file_path (the variation path). Without
    this view, the artisan has no way to set order_product at creation,
    and the approve branch always falls through to the variation path.
    See the CUSTOM pipeline v2 handoff.

    Only applies to CUSTOM digital lines. Non-CUSTOM lines 404 — the
    dashboard hides the button, and the check here closes the
    forged-POST path. A line whose fulfilled_by is not this artisan
    also 404s (get_object_or_404 with the ownership filter), so a
    guessed id cannot stage a file against another artisan's order.
    """
    profile = request.user.creator_profile

    line = get_object_or_404(
        OrderProduct,
        id=order_product_id,
        fulfilled_by=profile,
    )

    # Forged-POST guard, mirroring the variation view's is_digital=True.
    if not (
        line.product.is_digital
        and line.product.digital_fulfillment_type == "CUSTOM"
    ):
        raise Http404(
            "This order line is not a CUSTOM digital line."
        )

    product = line.product
    variation = line.product_variation

    pending_partial = "artisans/dashboard/partials/_pending_custom_digital_rows.html"
    form_template = "artisans/dashboard/partials/_vault_upload_form.html"

    # The form template renders into #vault-upload-modal-body on the
    # variation page; on the orders dashboard it targets
    # #order-product-vault-upload-modal-body. Keep the two containers
    # separate so the two modals can be open on different pages without
    # cross-targeting.
    form_context = {
        "form": None,  # filled per branch below
        "product": product,
        "variation": variation,
        "order_product": line,
        "upload_post_url": reverse(
            "a_dashboard_order_product_upload_vault",
            args=[order_product_id],
        ),
        "upload_target": "#order-product-vault-upload-modal-body",
    }

    if request.method == "POST":
        form = ArtisanVaultUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                self_supersede_and_create(
                    profile=profile,
                    product=product,
                    variation=variation,
                    form=form,
                    order_product=line,
                )
            except IntegrityError:
                # Race with a concurrent upload for the same order_product
                # from another tab. The partial unique constraint is the
                # guard; the correct recovery is to retry the supersession
                # once (the second call's select_for_update will see the
                # committed PENDING row and flip it to SUPERSEDED before
                # creating the new one). If the retry also fails
                # (three-way race, e.g. a third tab), the exception
                # propagates and the view returns 500 — acceptable
                # for a behaviour this rare; the constraint has still
                # protected the data.
                self_supersede_and_create(
                    profile=profile,
                    product=product,
                    variation=variation,
                    form=form,
                    order_product=line,
                )
            # Fetch the new PENDING row to schedule the admin notification.
            # Safe immediately after the helper returns: the second
            # partial unique constraint caps PENDING rows at one per
            # order_product, so .get() cannot race here.
            new_upload = ArtisanVaultUpload.objects.get(
                order_product=line, status="PENDING",
            )
            transaction.on_commit(
                lambda uid=new_upload.id:
                    send_vault_upload_pending_email_task.delay(str(uid))
            )
            messages.success(
                request,
                "已提交，等待管理員審核。｜Submitted for admin review.",
            )
            # Re-render the pending-custom-digital list so the card
            # picks up the new 待審核檔案 badge (see commit 5's
            # property on OrderProduct). The container id matches the
            # one in _orders_panel.html.
            pending_lines = (
                OrderProduct.objects
                .filter(fulfilled_by=profile, is_dispatched=False)
                .filter(
                    product__is_digital=True,
                    product__digital_fulfillment_type="CUSTOM",
                )
                .select_related("order", "product", "product_variation")
                .order_by("-order__created_at")
            )
            response = render(request, pending_partial, {
                "pending_custom_digital": pending_lines,
            })
            response["HX-Retarget"] = "#pending-custom-digital-container"
            response["HX-Trigger"] = json.dumps({
                "orderProductVaultUploadSuccess": True,
            })
            return response

        form_context["form"] = form
        return render(request, form_template, form_context)

    # GET
    form_context["form"] = ArtisanVaultUploadForm()
    return render(request, form_template, form_context)


@artisan_required
def dashboard_settlements(request):
    """
    Read-only list of settlement lines for the logged-in artisan.
    The net payable amount is only shown when is_finalised=True.
    """
    profile = request.user.creator_profile
    
    settlement_lines = (
        ArtisanSettlementLine.objects
        .filter(artisan=profile)
        .select_related('order')
        .order_by('-created_at')
    )

    context = artisan_dashboard_context(request)
    context.update({
        'active_section': 'settlements',
        'settlement_lines': settlement_lines,
        'page_title': 'Settlements｜結算',
    })

    if request.headers.get('HX-Request'):
        return render(request, 'artisans/dashboard/partials/_settlements_panel.html', context)
    return render(request, 'artisans/dashboard/settlements.html', context)