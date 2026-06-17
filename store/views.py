from django.shortcuts import render, get_object_or_404
from django.db.models import Exists, OuterRef, Q, Min
from .models import Product, ProductVariation
from category.models import Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, JsonResponse, FileResponse
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


def product(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug)
        single_product.tags_string = ",".join(single_product.tags.names())
        variations = single_product.variations.all()
        sizes = single_product.variations.values_list('size__size_name', flat=True).distinct().exclude(size=None)
        colors = single_product.variations.values_list('color__color_name', flat=True).distinct().exclude(color=None)
        types = single_product.variations.values_list('type__type_name', flat=True).distinct().exclude(type=None)
        min_price = min([variation.price for variation in variations])

        # Check current cart
        current_session_key = _cart_id(request)

        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            cart = Cart.objects.filter(cart_id=current_session_key, user__isnull=True).first()

        if not cart:
            cart = None
            
        variations_json = {}
        for variation in variations:
            variations_json[variation.pk] = {
                "color": variation.color.color_name if variation.color else None,
                "size": variation.size.size_name if variation.size else None,
                "type": variation.type.type_name if variation.type else None,
                "sku": variation.get_sku(),
                "price": variation.price,
                "stock": variation.stock,
                "image": variation.images.url,
                "in_cart": True if CartItem.objects.filter(cart=cart, product_variation=variation, is_active=True).exists() else False,
                "quantity_in_cart": CartItem.objects.get(cart=cart, product_variation=variation, is_active=True).quantity if CartItem.objects.filter(cart=cart, product_variation=variation, is_active=True).exists() else 0
            }

        domain = get_current_site(request).domain
        absolute_url = f"https://{domain}{single_product.get_url()}"

        product_gallery = single_product.productgallery_set.all()
        product_gallery_data = [
            {"href": item.image.url, "title": item.title} 
            for item in product_gallery
        ]
        product_gallery_data.insert(0, {"href": single_product.images.url, "title": single_product.product_name})

        variations_gallery_data = []
        for variation in variations:
            variation_gallery = variation.productvariationgallery_set.all()
            variation.variation_gallery_data = [
                {"id": variation.id},
                [
                    {"href": item.image.url, "title": item.title}
                    for item in variation_gallery
                ]
            ]
            # variation.variation_gallery_data[1].insert(0, {"href": variation.images.url, "title": variation.get_sku()})
            variations_gallery_data.append(variation.variation_gallery_data)
        
    except Exception as e:
        raise e

    context = {
        "single_product": single_product,
        "variations": variations,
        "variations_json": variations_json,
        "min_price": min_price,
        "sizes": sizes,
        "colors": colors,
        "types": types,
        "page_title": f"{single_product.product_name}｜Product",
        "absolute_url": absolute_url,
        "product_gallery": product_gallery,
        "product_gallery_json_data": product_gallery_data,
        "variations_gallery_json_data": variations_gallery_data,
        "main_title": "Item Details｜寶 貝 詳 情",
        "sub_title_1": "Plum lacks the snow's three parts of white, yet snow yields to the plum's delight.<br/>梅須遜雪三分白 雪卻輸梅一段香",
        "bread_crumb_1": "首頁 | Home",
        "bread_crumb_2": "寶貝們 | Products",
        "bread_crumb_4": single_product.product_name,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products/all",
        "bread_crumb_4_url": f"/store/product/{category_slug}/{product_slug}",
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
