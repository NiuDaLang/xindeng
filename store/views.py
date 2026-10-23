# store/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Exists, OuterRef, Q, Min
from .models import Product, ProductVariation, ProductGallery
from category.models import Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, JsonResponse, FileResponse, HttpResponse
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.contrib.sites.shortcuts import get_current_site
from taggit.models import Tag
from decimal import Decimal
from .models import DigitalDownloadToken
import os
import mimetypes
from django.conf import settings
from django.contrib.auth.decorators import login_required
from reviews.views import check_user_has_purchased_product
from reviews.models import Comment
from django.contrib.contenttypes.models import ContentType
from accounts.models import UserProfile
from django.shortcuts import redirect
from pathlib import Path
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from orders.models import OrderProduct
from creators.models import CreatorProfile
from core.image_utils import safe_image_url
from django.views.decorators.http import require_POST, require_GET
from accounts.decorators import superuser_required
from .tasks import (
    send_product_review_result_email_task,
    send_vault_upload_rejected_email_task,
)
from .models import ProductReviewLog

import shutil

import logging
logger = logging.getLogger(__name__)

def products(request, category_slug=None):
    try:
        if category_slug == "all":
            available_products = Product.products.all_available(variation_model=ProductVariation)
            available_products_with_stock = Product.products.all_available_with_stock()
            crumb_3 = "All | 所有"

        elif category_slug == "physical":
            available_products = Product.products.available_by_category_format(category_slug="physical")
            available_products_with_stock = Product.products.available_by_category_format_with_stock(category_slug="physical")
            crumb_3 = "physical | 實物"

        elif category_slug == "e-product":
            available_products = Product.products.available_by_category_format(category_slug="e-product")
            available_products_with_stock = Product.products.available_by_category_format_with_stock(category_slug="e-product")
            crumb_3 = "product | 電子產品"

        else:
            available_products = Product.products.available_by_category(category_slug=category_slug, variation_model=ProductVariation)
            available_products_with_stock = Product.products.available_by_category_with_stock(category_slug=category_slug)
            crumb_3 = get_object_or_404(Category, slug=category_slug).category_name

        available_tags = Tag.objects.filter(product__in=available_products).distinct()
    
    except Product.DoesNotExist or Category.DoesNotExist:
        raise Http404("No products found")

    # ────────────────────────────────────────────────────────────
    # 🌟 INSERT CREATOR FILTER HERE
    # ────────────────────────────────────────────────────────────
    creator_slug = request.GET.get('creator', '').strip()
    active_creator = None
    if creator_slug:
        active_creator = CreatorProfile.objects.filter(
            slug=creator_slug,
            is_verified=True,
        ).first()
        if active_creator:
            available_products = available_products.filter(creator=active_creator)
            available_products_with_stock = available_products_with_stock.filter(creator=active_creator)

    # ────────────────────────────────────────────────────────────
    # Continue with the existing pipeline
    # ────────────────────────────────────────────────────────────
    available_products_with_lowest_prices = Product.products.lowest_prices(available_products)

    # pagination
    paginator = Paginator(available_products_with_lowest_prices, 8)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = paged_products.count

    # Fetch approved product reviews for sidebar display
    product_content_type = ContentType.objects.get_for_model(Product)
    # Grab the latest 5 approved comments/reviews linked to products in this category
    sidebar_reviews = Comment.objects.filter(
        content_type=product_content_type,
        object_id__in=available_products.values_list('id', flat=True),
        is_approved=True
    ).select_related('user').order_by('-created_at')[:5]

    # Ensure every reviewer has a UserProfile instance so the template can safely access profile_picture
    reviewer_ids = [c.user_id for c in sidebar_reviews]
    existing_profile_user_ids = set(
        UserProfile.objects.filter(user_id__in=reviewer_ids).values_list('user_id', flat=True)
    )
    missing_profiles = [UserProfile(user_id=uid) for uid in reviewer_ids if uid not in existing_profile_user_ids]
    if missing_profiles:
        UserProfile.objects.bulk_create(missing_profiles, ignore_conflicts=True)

    # 🌟 FIX: Re-fetch with profile joined AND prefetch the Generic Foreign Key targets
    product_reviews = Comment.objects.filter(
        id__in=[c.id for c in sidebar_reviews]
    ).select_related('user__profile').prefetch_related('content_object').order_by('-created_at')

    context = {
        "category": category_slug,
        "available_products": paged_products,
        "product_count": product_count,
        "available_products_with_stock": available_products_with_stock,
        "active_creator": active_creator,
        "page_title": "寶貝們｜Products", 
        "main_title": "寶貝們｜Products",
        "sub_title_1": "海闊天空 尋覓您的摯愛",
        "bread_crumb_1": "首頁｜Home",
        "bread_crumb_2": "寶貝們｜Products",
        "bread_crumb_3": crumb_3,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products/all",
        "bread_crumb_3_url": f"/store/products/{category_slug}",
        "available_tags": available_tags,
        "product_reviews": product_reviews,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'store/partials/_products_region.html', context)

    return render(request,'store/products.html', context)


# htmx
def product(request, category_slug, product_slug):
    # Superusers can preview non-published / soft-deleted products
    if request.user.is_authenticated and getattr(request.user, "is_superadmin", False):
        single_product = get_object_or_404(Product, slug=product_slug)
    else:
        single_product = get_object_or_404(Product, slug=product_slug, is_active=True)

    single_product.tags_string = ",".join(single_product.tags.names())
    variations = single_product.variations.filter(is_available=True)
    min_price = min([v.price for v in variations]) if variations.exists() else 0.00
    only_one_variation = len(variations) == 1

    # Build default master product gallery list maps. safe_image_url
    # handles variations/products with no hero image, matching the
    # template-level fallback in product_form.html / gallery_partial.html.
    product_gallery = single_product.productgallery_set.all()
    default_gallery_list = [
        {"href": safe_image_url(item.image), "title": item.title}
        for item in product_gallery
    ]
    default_gallery_list.insert(
        0,
        {"href": safe_image_url(single_product.images), "title": single_product.product_name},
    )

    # Prepare variations stock counts for initial entry
    session_cart_key = _cart_id(request)
    cart = Cart.objects.filter(user=request.user).first() if request.user.is_authenticated else Cart.objects.filter(cart_id=session_cart_key, user__isnull=True).first()

    for var in variations:
        in_cart_item = (
            CartItem.objects
            .filter(cart=cart, product_variation=var, is_active=True)
            .first()
            if cart else None
        )
        qty_in_cart = in_cart_item.quantity if in_cart_item else 0
        var.available_production_stock = var.compute_available_stock(qty_in_cart)
        # Exposed to the template so the tooltip can show "in cart"
        # instead of the SKU when it applies.
        var.in_cart = bool(in_cart_item)

    exclusion_blacklist = [None, "", "NONE", "N/A", "N/A｜不適用", "N/A｜不適用"]
    has_valid_colors, has_valid_sizes, has_valid_types = False, False, False

    for var in variations:
        color_val = str(var.color.color_name).strip() if var.color else ""
        size_val = str(var.size.size_name).strip() if var.size else ""
        type_val = str(var.type.type_name).strip() if var.type else ""
        if color_val and color_val not in exclusion_blacklist: has_valid_colors = True
        if size_val and size_val not in exclusion_blacklist: has_valid_sizes = True
        if type_val and type_val not in exclusion_blacklist: has_valid_types = True

    has_any_valid_specifications = has_valid_colors or has_valid_sizes or has_valid_types

    # Fetch and filter historical review entries generic to this product
    product_content_type = ContentType.objects.get_for_model(single_product)
    reviews_list = Comment.objects.filter(content_type=product_content_type, object_id=single_product.id, is_approved=True)

    has_purchased_product_flag = False
    has_already_reviewed_flag = False

    if request.user.is_authenticated:
        # 1. Ensure UserProfile exists
        UserProfile.objects.get_or_create(user=request.user)
        
        # 2. Check if user already reviewed
        has_already_reviewed_flag = Comment.objects.filter(
            user=request.user, 
            content_type=product_content_type, 
            object_id=single_product.id
        ).exists()
        
        # 3. Assume you have a helper function to check purchase
        has_purchased_product_flag = check_user_has_purchased_product(request.user, single_product.id)

    # Flag for template: Can only review if purchased AND not already reviewed
    user_can_review_flag = has_purchased_product_flag and not has_already_reviewed_flag

    context = {
        "single_product": single_product,
        "variations": variations,
        "displayed_price": min_price,
        "only_one_variation": only_one_variation,
        "selected_var_id": None,
        "is_resolved_sku": False,
        "current_main_image": safe_image_url(single_product.images),
        "product_gallery": default_gallery_list,
        "has_valid_colors": has_valid_colors,
        "has_valid_sizes": has_valid_sizes,
        "has_valid_types": has_valid_types,
        "has_any_valid_specifications": has_any_valid_specifications,
        
        # 🌟 RESTORED: Verified purchase flag calculation injected for base view
        "has_purchased_product_flag": check_user_has_purchased_product(request.user, single_product.id),
        "reviews_list": reviews_list,
        "has_already_reviewed_flag": has_already_reviewed_flag,
        "user_can_review_flag": user_can_review_flag,

        "active_filters": {"size": "Tap image｜點選圖像 ↑", "color": "Tap image｜點選圖像 ↑", "type": "Tap image｜點選圖像 ↑"},
        "page_title": f"{single_product.product_name}｜XinDeng Art Shop",
        "absolute_url": request.build_absolute_uri(single_product.get_url()),
        "main_title": "Item Details｜寶貝詳情",
        "sub_title_2": "梅須遜雪三分白 雪卻輸梅一段香",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Products｜寶貝們",
        "bread_crumb_4": single_product.product_name,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products/all",
    }
    return render(request, 'store/product.html', context)


def filter_products(request):
    category = request.GET.get('category')
    color = request.GET.get('color')
    selected_tag_ids = request.GET.getlist('tags')
    price_range = request.GET.get('price_range')
    params = [category, color, selected_tag_ids, price_range]

    qs = Product.products.filter(is_active=True).annotate(
        min_price=Min(
            'variations__price', 
            filter=Q(variations__is_available=True)
        )
    )
    # Use Q objects to build an "OR" filter
    filters = Q()

    if category:
        filters &= Q(category__slug=category)
    if color:
        filters &= Q(color=color)
    if selected_tag_ids:
        filters &= Q(tags__id__in=selected_tag_ids)
    if price_range:
        filters &= Q(min_price__lte=Decimal(price_range))

    if filters:
        filtered_products = qs.filter(filters).distinct().order_by('product_name')
        if (filtered_products.exists()):
            filtered_products_json = []
            for product in filtered_products:
                filtered_products_json.append({
                    "product_name": product.product_name,
                    "description": product.description,
                    "image_url": safe_image_url(product.images),
                    "price": float(product.min_price),
                    "tags": list(product.tags.values_list('name', flat=True)),
                    "url": product.get_url(),
                })
            return JsonResponse({"filtered_products_json": filtered_products_json})
        else:
            return JsonResponse({"filtered_products_json": []})
    else:
        # If no filters were applied, maybe return everything or none
        return JsonResponse({"filtered_products_json": []})
    

@login_required(login_url='login')
def secure_file_download_gate(request, token_id):
    """
    Time-Locked Data Stream Matrix:
    Validates token expirations and streams raw binary safely from the local secure disk structure.
    Also flags digital assets as claimed to block subsequent customer order cancellations.
    File resolution: prefer OrderProduct.digital_file_path (CUSTOM delivery); 
    fall back to ProductVariation.digital_file_path (INSTANT delivery). 
    Both are vault-relative. See the CUSTOM pipeline v2 handoff for why the two pointers exist.
    """

    # Fetch by id only. Ownership is enforced explicitly below so the
    # guest path can fall back to an email match when token.user is
    # None. The old single-arg lookup get_object_or_404(..., user=...)
    # collapsed fetch and ownership into one query; splitting them is
    # what makes the guest branch possible without changing the member
    # branch's observable behaviour.
    token = get_object_or_404(DigitalDownloadToken, id=token_id)

    # ── Authorisation ─────────────────────────────────────────────
    # Member tokens: exact user match. Same outcome as before — a
    # different authenticated user sees 404, not 403, so the gate
    # does not leak that the token exists.
    if token.user_id is not None:
        if token.user_id != request.user.id:
            raise Http404("Token not found for this user.")

    # Guest tokens: no user FK to match against. The identity anchor is
    # the email snapshot taken at issue time. The login_required
    # decorator guarantees an authenticated user here; we additionally
    # require that token.email is non-empty and matches the request
    # user's email case-insensitively.
    #
    # The `if not token_email` guard is load-bearing: without it, an
    # Account with an empty email string would match a token whose
    # email is also empty, granting access to anyone who happened to
    # log in with a blank email. Fail closed.
    #
    # Invariant this relies on: Account.email is unique (enforced by the
    # model field). If that ever changes — e.g. allauth config drift —
    # this fallback stops being a valid identity check and must be
    # revisited. See Roadmap #7.5.
    else:
        token_email = (token.email or "").strip().lower()
        user_email = (request.user.email or "").strip().lower()
        if not token_email or token_email != user_email:
            raise Http404("Token not found for this user.")

    if token.is_revoked_or_expired:
        # Distinguish cancellation-revocation from ordinary time-expiry.
        # `is_revoked` is True when the token was explicitly deactivated
        # (either by admin revocation or by the cancellation pipeline);
        # `is_expired` is True only when wall-clock has passed expires_at.
        is_revoked_by_cancellation = (
            token.is_revoked
            or (token.order_product.order.order_status == 'Cancelled')
        )

        if is_revoked_by_cancellation:
            context = {
                "page_title": "Access Revoked ｜ 存取權限已取消",
                "error_headline": "Download Access Revoked ｜ 下載權限已撤銷",
                "error_message": "This secure download link has been deactivated because the associated order was cancelled or refunded. Future access is permanently restricted.",
                "error_message_cn": "此安全下載連結已失效，原因為其關聯之訂單已辦理取消或退款手續。該檔案之線上存取權限已永久終止。",
                "is_cancelled_or_revoked": True
            }
        else:
            context = {
                "page_title": "Link Expired ｜ 連結已失效",
                "error_headline": "Download Link Expired ｜ 下載連結已失效",
                "error_message": f"This secure link expired on {token.expires_at.strftime('%Y-%m-%d %H:%M')} (7-day access window closed). Please contact customer support to request a new download pass.",
                "error_message_cn": f"此安全連結已於 {token.expires_at.strftime('%Y-%m-%d %H:%M')} 超時失效（7天開放下載視窗已關閉）。請聯絡客服人員為您手動重置下載連結。",
                "is_cancelled_or_revoked": False
            }
        return render(request, "store/digital_download_error.html", context, status=403)

    order_product = token.order_product
    variation = order_product.product_variation

    # ── FILE RESOLUTION ───────────────────────────────────────────────
    # CUSTOM path: per-order-product pointer, populated by
    # review_vault_upload_approve when the upload was order-product-
    # scoped. Takes precedence when set.
    #
    # INSTANT path: variation-level pointer, the original behaviour.
    #
    # Fail closed: if neither pointer is set, 404. This is the same
    # shape as the original single-pointer check, extended to
    # consider the order-product pointer first.
    #
    # Precedence rule: the order-product pointer wins when set. This
    # is what makes CUSTOM delivery correct — the order-product
    # pointer is the per-order file, the variation pointer is the
    # shared one. A future refactor that "simplifies" this back to a
    # single-pointer lookup breaks CUSTOM delivery. See the CUSTOM
    # pipeline v2 handoff.
    file_pointer = (order_product.digital_file_path or "").strip()
    if not file_pointer and variation:
        file_pointer = (variation.digital_file_path or "").strip()
    if not file_pointer:
        raise Http404(
            "Digital file resource target is not registered for this line."
        )

    # ── SECURE PATH RESOLUTION ────────────────────────────────────────
    # Anchor the vault from settings rather than hard-coding BASE_DIR so
    # the location is configurable per-deployment and overridable in tests.
    vault_root = Path(settings.XINDENG_VAULT_ROOT).resolve()
    raw_target = vault_root / file_pointer

    # Reject symlinks outright. Rationale: resolve() follows symlinks, so
    # a symlink pointing outside the vault would already fail the
    # containment check below; a symlink pointing *inside* the vault
    # would pass it. Refusing both is simpler to reason about than
    # auditing which symlinks are "safe". A private vault should never
    # contain symlinks anyway.
    if raw_target.is_symlink():
        raise Http404("Symlink not permitted in vault.")

    target = raw_target.resolve()

    # Containment check — post-resolution, so any symlinked intermediate
    # directory is caught too. is_relative_to() is exact for the
    # "target == vault_root" case, unlike a `parents` check.
    if not target.is_relative_to(vault_root):
        raise Http404("Directory traversal security exception occurred.")

    if not target.is_file():
        raise Http404("The requested file asset could not be found on this disk node.")

    # DIGITAL ASSET UNIFIED CLAIM LOCK ENGINE
    if not order_product.is_claimed:
        try:
            with transaction.atomic():
                order_product = OrderProduct.objects.select_for_update().get(id=order_product.id)
                order_product.is_claimed = True
                order_product.claim_timestamp = timezone.now()
                order_product.save(update_fields=['is_claimed', 'claim_timestamp', 'updated_at'])
        except Exception as e:
            messages.error(request, f"Claim status locking transaction failed: {str(e)}")
            return redirect('dashboard', subpage='main')

    response = FileResponse(open(target, 'rb'), as_attachment=True)

    mime_type, _ = mimetypes.guess_type(str(target))
    response['Content-Type'] = mime_type or 'application/octet-stream'

    return response


# ═══════════════════════════════════════════════════════════════
# SUPERUSER PRODUCT REVIEW — Stage P-C
# ═══════════════════════════════════════════════════════════════

@require_POST
@superuser_required
def review_product_approve(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.status != "Pending":
        messages.error(request, "此作品不在待審核狀態。｜Product is not pending review.")
        return redirect("dashboard", subpage="product_review")

    with transaction.atomic():
        product.status = "Published"
        product.is_active = True
        product.save(update_fields=["status", "is_active", "modified_date"])

        ProductReviewLog.objects.create(
            product=product,
            action="approved",
            actor=request.user,
            note="",
        )

    transaction.on_commit(
        lambda: send_product_review_result_email_task.delay(product.id, True, "")
    )
    messages.success(request, f"已通過：{product.product_name}｜Approved.")
    return redirect("dashboard", subpage="product_review")


@require_POST
@superuser_required
def review_vault_upload_approve(request, upload_id):
    """
    Approve a staged ArtisanVaultUpload.

    Moves the staged file from _pending/ into the vault root, updates
    ProductVariation.digital_file_path, and records the approval in
    VaultUploadReviewLog.

    The file move happens inside the transaction, before the DB writes.
    If a DB write fails, we compensate by renaming the file back to
    _pending/. Rationale: a rolled-back transaction with an already-moved
    file would leave an orphan in the vault root; a rolled-back
    transaction with the file restored is a clean no-op from the
    observer's perspective.

    A crash between the rename and the commit is the only unsolved
    failure mode — it leaves a file in the vault with no pointer. The
    _pending/ sweeper (a future commit) will not catch this; a separate
    reconciliation command will be needed once the vault runs in anger.
    """
    from store.models import ArtisanVaultUpload, VaultUploadReviewLog

    upload = get_object_or_404(ArtisanVaultUpload, id=upload_id)

    if upload.status != "PENDING":
        messages.error(
            request,
            "此檔案不在待審核狀態。｜This upload is not pending review.",
        )
        return redirect("dashboard", subpage="product_review")

    if upload.storage_kind == "EXTERNAL_PENDING":
        messages.error(
            request,
            "此檔案尚未從雲端複製至本機，無法審核。"
            "｜This cloud-drive upload has not been copied locally yet; "
            "stage it first.",
        )
        return redirect("dashboard", subpage="product_review")

    if not upload.staged_filename:
        messages.error(
            request,
            "此上傳缺少檔案路徑，無法審核。"
            "｜This upload has no staged file; cannot approve.",
        )
        return redirect("dashboard", subpage="product_review")

    vault_root = Path(settings.XINDENG_VAULT_ROOT)
    pending_root = vault_root / "_pending"
    retired_root = vault_root / "_retired"

    src_path = pending_root / upload.staged_filename
    dst_path = vault_root / upload.staged_filename

    if not src_path.is_file():
        messages.error(
            request,
            "找不到待審檔案，可能已被其他程序處理。"
            "｜Staged file not found; it may have already been processed.",
        )
        return redirect("dashboard", subpage="product_review")

    variation = upload.variation
    is_order_product_scoped = upload.order_product_id is not None

    # The "previous pointer to retire" depends on which scope this
    # upload belongs to. CUSTOM uploads promote the file to the
    # order-product; INSTANT uploads promote to the variation. The
    # two scopes are mutually exclusive on an individual upload row
    # (a row is either variation-scoped or order-product-scoped), so
    # the branch below is exhaustive.
    if is_order_product_scoped:
        previous_pointer = upload.order_product.digital_file_path or ""
    else:
        previous_pointer = variation.digital_file_path or ""

    try:
        with transaction.atomic():
            # ── Lock the upload and variation rows ───────────────
            locked_upload = (
                ArtisanVaultUpload.objects
                .select_for_update()
                .get(id=upload.id)
            )
            if locked_upload.status != "PENDING":
                # Another reviewer beat us to it.
                messages.error(
                    request,
                    "此上傳已被其他審核者處理。"
                    "｜This upload was processed by another reviewer.",
                )
                return redirect("dashboard", subpage="product_review")

            locked_variation = (
                ProductVariation.objects
                .select_for_update()
                .get(id=variation.id)
            )

            # ── Retire the previous file, if any ─────────────────
            # Do this before the rename so a failure here aborts
            # without having touched the new file.
            if (
                previous_pointer
                and previous_pointer != upload.staged_filename
            ):
                previous_path = vault_root / previous_pointer
                if previous_path.is_file():
                    retired_root.mkdir(parents=True, exist_ok=True)
                    retired_path = retired_root / previous_pointer
                    retired_path.parent.mkdir(parents=True, exist_ok=True)
                    # If the retired path already exists (a repeat
                    # approval of the same old pointer), suffix it.
                    if retired_path.exists():
                        retired_path = (
                            retired_root
                            / f"{previous_path.stem}.{int(timezone.now().timestamp())}"
                            f"{previous_path.suffix}"
                        )
                    shutil.move(str(previous_path), str(retired_path))

            # ── Move the new file into the vault root ────────────
            # Same-filesystem rename: atomic on POSIX.
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            os.rename(src_path, dst_path)

            # ── DB writes ─────────────────────────────────────────
            # Lock ordering (write-side): upload → variation →
            # order-product. No other code path locks the variation
            # and the order-product together, so this ordering is
            # uncontended. Named in the CUSTOM pipeline v2 handoff.
            try:
                if is_order_product_scoped:
                    locked_order_product = (
                        OrderProduct.objects
                        .select_for_update()
                        .get(id=locked_upload.order_product_id)
                    )
                    locked_order_product.digital_file_path = (
                        locked_upload.staged_filename
                    )
                    locked_order_product.save(
                        update_fields=["digital_file_path"]
                    )
                    # Issue the token now that the file pointer is
                    # committed inside this transaction. Same helper
                    # as the three INSTANT call sites; the token row
                    # and is_dispatched flip are written immediately
                    # and roll back with the transaction if anything
                    # downstream fails. The email dispatch is deferred
                    # to on_commit by the helper itself — unchanged
                    # behaviour.
                    from orders.utils import issue_download_token #DO NOT MAKE THIS IMPORT MODULE-SCOPE
                    # CUSTOM delivery is made-to-order: the customer waited weeks
                    # for the work. The 2026-10-21 decision specifies one year,
                    # not the shared helper's 7-day default (which is the INSTANT
                    # window and is meaningful there — the download-period /
                    # cancellation-window shape). See the CUSTOM pipeline v2
                    # handoff, and the email-template branch that must move with
                    # this call.
                    issue_download_token(locked_order_product, ttl_hours=8760)
                else:
                    locked_variation.digital_file_path = (
                        locked_upload.staged_filename
                    )
                    locked_variation.save(
                        update_fields=["digital_file_path"]
                    )

                locked_upload.status = "APPROVED"
                locked_upload.reviewed_at = timezone.now()
                locked_upload.reviewed_by = request.user
                locked_upload.save(
                    update_fields=["status", "reviewed_at", "reviewed_by"],
                )

                VaultUploadReviewLog.objects.create(
                    upload=locked_upload,
                    action="approved",
                    actor=request.user,
                    note="",
                )
            except Exception:
                # Compensating action: put the file back where it
                # came from so a rolled-back transaction leaves the
                # filesystem unchanged. Same as before; the branch
                # does not change the compensating behaviour.
                try:
                    os.rename(dst_path, src_path)
                except OSError as rename_back_err:
                    logger.error(
                        "Vault approve: failed to restore %s to %s after "
                        "DB error: %s",
                        dst_path, src_path, rename_back_err,
                    )
                raise

    except Exception as exc:
        messages.error(
            request,
            f"審核時發生錯誤，已安全撤回。｜Approval failed and was rolled back: {exc}",
        )
        return redirect("dashboard", subpage="product_review")

    messages.success(
        request,
        f"已通過：{variation.get_sku()}｜Approved.",
    )
    return redirect("dashboard", subpage="product_review")


@require_GET
@superuser_required
def review_vault_upload_preview(request, upload_id):
    """
    Stream the staged file of a PENDING ArtisanVaultUpload to the
    reviewing superuser, without moving it out of _pending/.

    This is the admin-side counterpart of secure_file_download_gate.
    The gate serves the customer the final, approved file. This view
    serves the reviewer the staged file so they can decide whether to
    approve it. Same containment discipline; different authorisation
    target (the reviewer, not the token holder) and different source
    (the _pending/ staging area, not the vault root).

    Only PENDING uploads are served. Once an upload is approved or
    rejected, the file has either moved to the vault root (approved,
    served by the gate to the customer) or been deleted (rejected);
    serving it here would either be dead code or a leak of a deleted
    path. Restricting to PENDING keeps the view single-purpose.

    Content-Disposition branches on whether the browser can render
    the file natively:

      * application/pdf  → inline. Chrome, Firefox, Safari, and Edge
        all ship a PDF viewer. The reviewer reads the file in the
        tab and closes it.

      * application/epub+zip, application/zip → attachment. No browser
        renders EPUB or ZIP natively; inline would show a blank page
        (what the reviewer then assumes is a broken view). Forcing
        download is the correct intent: the reviewer wants the file
        in their hands, not in the browser window.

    A future addition (e.g. accepting image formats as an alternate
    review path) would extend the inline branch; the ZIP/EPUB branch
    stays attachment.
    """
    from store.models import ArtisanVaultUpload

    upload = get_object_or_404(ArtisanVaultUpload, id=upload_id)

    if upload.status != "PENDING":
        raise Http404(
            "Only PENDING uploads can be previewed by the reviewer."
        )

    if not upload.staged_filename:
        raise Http404(
            "This upload has no staged file to preview."
        )

    pending_root = Path(settings.XINDENG_VAULT_ROOT) / "_pending"
    raw_target = pending_root / upload.staged_filename

    if raw_target.is_symlink():
        raise Http404("Symlink not permitted in vault.")

    target = raw_target.resolve()
    if not target.is_relative_to(pending_root.resolve()):
        raise Http404("Directory traversal security exception occurred.")

    if not target.is_file():
        raise Http404("Staged file not found on disk.")

    mime_type, _ = mimetypes.guess_type(str(target))
    mime_type = mime_type or "application/octet-stream"

    # Branches on whether the browser can render the file natively.
    # Only PDF has a browser-native renderer among the whitelisted
    # formats; ZIP and EPUB do not and would show a blank inline page.
    if mime_type == "application/pdf":
        disposition = "inline"
    else:
        disposition = "attachment"

    response = FileResponse(
        open(target, "rb"),
        as_attachment=(disposition == "attachment"),
    )
    response["Content-Type"] = mime_type
    response["Content-Disposition"] = (
        f'{disposition}; filename="{upload.original_filename or target.name}"'
    )
    return response


@require_POST
@superuser_required
def review_vault_upload_reject(request, upload_id):
    """
    Reject a staged ArtisanVaultUpload.

    Records the rejection with a required reason, then deletes the
    staged file on commit.

    Ordering note: unlike approval, the file deletion happens on
    transaction.on_commit() rather than inside the atomic block. A
    rejected file is being discarded, not promoted — if the DB write
    fails, the file lingers in _pending/ and nothing else changes,
    which is a benign leak the future sweeper will catch. Deleting
    first and then failing the DB write would leave a stale PENDING
    row pointing at a file that no longer exists, which is worse.
    """
    from store.models import ArtisanVaultUpload, VaultUploadReviewLog

    upload = get_object_or_404(ArtisanVaultUpload, id=upload_id)

    if upload.status != "PENDING":
        messages.error(
            request,
            "此檔案不在待審核狀態。｜This upload is not pending review.",
        )
        return redirect("dashboard", subpage="product_review")

    note = request.POST.get("note", "").strip()
    if not note:
        messages.error(
            request,
            "拒絕時必須填寫理由。｜A reason is required when rejecting.",
        )
        return redirect("dashboard", subpage="product_review")

    vault_root = Path(settings.XINDENG_VAULT_ROOT)
    pending_root = vault_root / "_pending"

    try:
        with transaction.atomic():
            locked_upload = (
                ArtisanVaultUpload.objects
                .select_for_update()
                .get(id=upload.id)
            )
            if locked_upload.status != "PENDING":
                messages.error(
                    request,
                    "此上傳已被其他審核者處理。"
                    "｜This upload was processed by another reviewer.",
                )
                return redirect("dashboard", subpage="product_review")

            locked_upload.status = "REJECTED"
            locked_upload.reviewed_at = timezone.now()
            locked_upload.reviewed_by = request.user
            locked_upload.review_note = note
            locked_upload.save(update_fields=[
                "status", "reviewed_at", "reviewed_by", "review_note",
            ])

            VaultUploadReviewLog.objects.create(
                upload=locked_upload,
                action="rejected",
                actor=request.user,
                note=note,
            )

            # ── Schedule staged-file deletion after commit ────────
            # Capture the values we need; do not close over the
            # instance, which may be modified further up the stack.
            staged_filename = locked_upload.staged_filename
            upload_id_for_email = str(locked_upload.id)
            if staged_filename:
                staged_path = pending_root / staged_filename

                def _delete_staged():
                    try:
                        staged_path.unlink(missing_ok=True)
                    except OSError as exc:
                        logger.warning(
                            "Reject: could not delete staged file %s: %s",
                            staged_path, exc,
                        )

                transaction.on_commit(_delete_staged)

            transaction.on_commit(
                lambda uid=upload_id_for_email:
                    send_vault_upload_rejected_email_task.delay(uid)
            )

    except Exception as exc:
        messages.error(
            request,
            f"審核時發生錯誤，已安全撤回。｜Rejection failed and was rolled back: {exc}",
        )
        return redirect("dashboard", subpage="product_review")

    messages.success(
        request,
        f"已拒絕：{upload.variation.get_sku()}｜Rejected.",
    )
    return redirect("dashboard", subpage="product_review")


@require_POST
@superuser_required
def review_product_reject(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.status != "Pending":
        messages.error(request, "此作品不在待審核狀態。｜Product is not pending review.")
        return redirect("dashboard", subpage="product_review")

    note = request.POST.get("note", "").strip()
    if not note:
        messages.error(request, "拒絕時必須填寫理由。｜A reason is required when rejecting.")
        return redirect("dashboard", subpage="product_review")

    with transaction.atomic():
        product.status = "Rejected"
        product.is_active = False
        product.save(update_fields=["status", "is_active", "modified_date"])

        ProductReviewLog.objects.create(
            product=product,
            action="rejected",
            actor=request.user,
            note=note,
        )

    transaction.on_commit(
        lambda: send_product_review_result_email_task.delay(product.id, False, note)
    )
    messages.success(request, f"已拒絕：{product.product_name}｜Rejected.")
    return redirect("dashboard", subpage="product_review")