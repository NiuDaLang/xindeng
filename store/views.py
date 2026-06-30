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


# Create your views here.
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

    available_products_with_lowest_prices = Product.products.lowest_prices(available_products)

    # pagination
    paginator = Paginator(available_products_with_lowest_prices, 8)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = paged_products.count

    context = {
        "category": category_slug,
        "available_products": paged_products,
        "product_count": product_count,
        "available_products_with_stock": available_products_with_stock,
        "page_title": "寶貝們｜Products", 
        "main_title": "寶貝們 | Products",
        "sub_title_1": "海闊天空 尋覓您的摯愛",
        "bread_crumb_1": "首頁 | Home",
        "bread_crumb_2": "寶貝們 | Products",
        "bread_crumb_3": crumb_3,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products/all",
        "bread_crumb_3_url": f"/store/products/{category_slug}",
        "available_tags": available_tags,
    }
    return render(request,'store/products.html', context)


# htmx
def product(request, category_slug, product_slug):
    single_product = get_object_or_404(Product, slug=product_slug, is_active=True)
    single_product.tags_string = ",".join(single_product.tags.names())
    variations = single_product.variations.filter(is_available=True)
    min_price = min([v.price for v in variations]) if variations.exists() else 0.00

    # Build default master product gallery list maps
    product_gallery = single_product.productgallery_set.all()
    default_gallery_list = [{"href": item.image.url, "title": item.title} for item in product_gallery]
    default_gallery_list.insert(0, {"href": single_product.images.url, "title": single_product.product_name})

    # Prepare variations stock counts for initial entry
    session_cart_key = _cart_id(request)
    cart = Cart.objects.filter(user=request.user).first() if request.user.is_authenticated else Cart.objects.filter(cart_id=session_cart_key, user__isnull=True).first()

    for var in variations:
        v_stock = var.stock
        if cart:
            in_cart_item = CartItem.objects.filter(cart=cart, product_variation=var, is_active=True).first()
            if in_cart_item:
                v_stock = max(0, v_stock - in_cart_item.quantity)
        var.available_production_stock = v_stock

    exclusion_blacklist = [None, "", "NONE", "N/A", "N/A｜不適用", "N/A ｜ 不適用"]
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
        "selected_var_id": None,
        "is_resolved_sku": False,
        "current_main_image": single_product.images.url,
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

        "active_filters": {"size": "點選上方圖像", "color": "點選上方圖像", "type": "點選上方圖像"},
        "page_title": f"{single_product.product_name} ｜ XinDeng Art Shop",
        "absolute_url": request.build_absolute_uri(single_product.get_url()),
        "main_title": "Item Details ｜ 寶貝詳情",
        "sub_title_2": "梅須遜雪三分白 雪卻輸梅一段香",
        "bread_crumb_1": "Home ｜ 首頁",
        "bread_crumb_2": "Products ｜ 寶貝們",
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
                    "image_url": product.images.url if product.images else None,
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
    """
    # Look up the token, ensuring it belongs explicitly to the logged-in customer profile
    token = get_object_or_404(DigitalDownloadToken, id=token_id, user=request.user)

    # 🌟 TRACK LINK EXPIRATION MATRIX
    if token.is_expired:
        context = {
            "page_title": "Link Expired ｜ 連結已失效",
            "error_headline": "Download Link Expired ｜ 下載連結已失效",
            "error_message": f"This secure link expired on {token.expires_at.strftime('%Y-%m-%d %H:%M')} (48-hour access window closed). Please contact customer support to request a new download pass.",
            "error_message_cn": f"此安全連結已於 {token.expires_at.strftime('%Y-%m-%d %H:%M')} 超時失效（48小時開放下載視窗已關閉）。請聯絡客服人員為您手動重置下載鏈接。"
        }
        return render(request, "store/digital_download_error.html", context, status=403)

    order_product = token.order_product
    variation = order_product.product_variation
    
    # Verify that a valid path string is registered inside your model row instance
    if not variation.digital_file_path:
        raise Http404("Digital file resource target is not registered in this variation system.")

    # 🌟 SECURE COORDINATES PATH RESOLUTION
    # Anchor path directly inside your unexposed private folder
    private_vault_root = os.path.join(settings.BASE_DIR, 'private_digital_vault')
    absolute_file_path = os.path.abspath(os.path.join(private_vault_root, variation.digital_file_path))

    # Security Check: Prevent directory traversal exploits
    if not absolute_file_path.startswith(private_vault_root):
        raise Http404("Directory traversal security exception occurred.")

    if not os.path.exists(absolute_file_path) or os.path.isdir(absolute_file_path):
        raise Http404("The requested file asset could not be found on this disk node.")

    # Track download metrics (Friendly option: allow multiple downloads within the 48 hours)
    # To strictly allow a single click only, toggle token.is_active = False here and run token.save()

    # Stream the file safely to the browser
    response = FileResponse(open(absolute_file_path, 'rb'), as_attachment=True)
    
    # Auto-detect Content-Type parameters cleanly (PDF, EPUB, ZIP, etc.)
    mime_type, _ = mimetypes.guess_type(absolute_file_path)
    response['Content-Type'] = mime_type or 'application/octet-stream'
    
    return response
