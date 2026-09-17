from django.shortcuts import render
from store.models import Product
from blog.models import Post
import random
from django.contrib.sites.shortcuts import get_current_site
from .utils import get_soul_number
from django.db.models import Q, Min, Count
from django.http import JsonResponse
from creators.models import CreatorProfile
from creators.utils import get_search_variants


def test(request):
    return render(request, 'pages/test.html')


def home(request):
    valid_products = Product.products.filter(
        is_active=True,
        variations__isnull=False,
        variations__is_available=True
    ).distinct() # Use .distinct() to prevent duplicate rows from the variation join

    # 2. Extract the safe ID list directly from the cleaned queryset pool
    product_ids = list(valid_products.values_list('id', flat=True))

    # 3. Handle a potential fallback safety guard if your active catalog drops below 6 items
    sample_size = min(len(product_ids), 6)
    if sample_size > 0:
        random_ids = random.sample(product_ids, sample_size)
    else:
        random_ids = []

    # 4. Pull the 6 random featured products AND aggregate their lowest price right inside the DB
    featured_products = Product.products.filter(id__in=random_ids).annotate(
        min_price=Min(
            'variations__price', 
            filter=Q(variations__is_available=True)
        ),
        # Generates a 'total_variations' integer attribute for each product row
        total_variations=Count(
            'variations',
            filter=Q(variations__is_available=True)
        )
    )

    # Attach your formatting parameters onto the object records
    for product in featured_products:
        if product.min_price is not None:
            # If total_variations is greater than 1, prepend your '~' character
            is_range = "~" if product.total_variations > 1 else ""
            product.formatted_price = f"{product.min_price:,.2f}{is_range}"
        else:
            product.formatted_price = "0.00"


    domain = get_current_site(request).domain
    absolute_url = f"https://{domain}"

    posts = Post.objects.all().order_by('-created_at')[:4]
    posts_json = {}
    for i, post in enumerate(posts):
        posts_json[i] = {
            "title": post.title,
            "short_description": post.short_description,
            "featured_image": post.featured_image.url,
            "url": post.get_url(),
        }    
        
    context = {
        "page_title": "Home｜首頁",
        "featured_products": featured_products,
        "absolute_url": absolute_url,
        "posts": posts,
        "posts_json": posts_json,
    }
    return render(request, 'home.html', context)


def about(request):
    context = {
        "page_title": "About Us｜關於我們",
        "main_title": "About Us｜關 於 我 們",
        "sub_title_1": "The Five Ws of Hṛdayadīpa｜心燈之屋的人事時地物",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "About Us｜關 於 我 們",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/about",
    }
    return render(request, 'pages/about.html', context)


def collaboration(request):
    context = {
        "page_title": "Collaboration｜與我們合作",
        "main_title": "Collab with Us｜與 我 們 合 作",
        "sub_title_1": "Weave together the gathering of light｜共同探討光的凝聚",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Collab｜合作",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/collaboration",
    }
    return render(request, 'pages/collaboration.html', context)


def contact(request):
    context = {
        "page_title": "Contact Us｜聯繫我們",
        "main_title": "Contact Us｜聯 繫 我 們",
        "sub_title_1": "應物空三世 隨緣遍十方",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "聯繫我們",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/contact",
        "bread_crumb_3_url": "",
    }
    return render(request, 'pages/contact.html', context)


def error_404(request, exception=None):
    """Custom 404 Not Found error page router view."""
    return render(request, '404.html', {"page_title": "404｜頁面不存在"}, status=404)


# Keep your 500 error handler exactly as it is (it only takes request)
def error_500(request):
    """Custom 500 Internal Server Error page router view."""
    return render(request, '500.html', {"page_title": "500｜系統錯誤"}, status=500)


def search(request):
    keyword = ""
    products = Product.objects.none()
    posts = Post.objects.none()
    creators = CreatorProfile.objects.none()
    product_count = 0
    post_count = 0
    creator_count = 0
    premium_creator_count = 0
    total_count = 0

    if "keyword" in request.GET:
        keyword = request.GET["keyword"].strip()
        if keyword:
            # 🌟 Get simplified + traditional + original variants
            variants = get_search_variants(keyword)

            # ── PRODUCTS ──────────────────────────────────────────
            product_q = Q()
            for v in variants:
                product_q |= (
                    Q(product_name__icontains=v) |
                    Q(details__icontains=v) |
                    Q(description__icontains=v) |
                    Q(brand__icontains=v) |
                    Q(category__category_name__icontains=v) |
                    Q(origin__icontains=v) |
                    Q(gender__icontains=v) |
                    Q(blood__icontains=v) |
                    Q(tags__name__icontains=v) |
                    Q(color__icontains=v) |
                    Q(creator__display_name__icontains=v)
                )

            products = (
                Product.objects
                .prefetch_related('variations', 'tags')
                .select_related('category', 'creator')
                .filter(
                    product_q & Q(is_active=True),
                    variations__isnull=False
                )
                .distinct()
                .order_by("-created_date")
            )
            product_count = products.count()

            # ── POSTS ─────────────────────────────────────────────
            post_q = Q()
            for v in variants:
                post_q |= (
                    Q(title__icontains=v) |
                    Q(short_description__icontains=v) |
                    Q(post_category__icontains=v) |
                    Q(author__username__icontains=v) |
                    Q(blog_body__icontains=v) |
                    Q(tags__name__icontains=v) |
                    Q(post_type__icontains=v) |
                    Q(creator__display_name__icontains=v)
                )

            posts = (
                Post.objects
                .filter(post_q & Q(status="Published"))
                .distinct()
            )
            post_count = posts.count()

            # ── CREATORS ──────────────────────────────────────────
            creator_q = Q()
            for v in variants:
                creator_q |= (
                    Q(display_name__icontains=v) |
                    Q(tagline__icontains=v) |
                    Q(bio__icontains=v) |
                    Q(province__icontains=v) |
                    Q(city__icontains=v) |
                    Q(craft_types__name__icontains=v) |
                    Q(craft_types__label__icontains=v) |
                    Q(tags__name__icontains=v)
                )

            creators = (
                CreatorProfile.objects
                .filter(is_verified=True)
                .filter(creator_q)
                .prefetch_related('tags')
                .distinct()
                .order_by('-is_premium', 'display_name')
            )
            creator_count = creators.count()
            premium_creator_count = creators.filter(is_premium=True).count()

            total_count = product_count + post_count + creator_count

    context = {
        "total_count": total_count,
        "products": products,
        "product_count": product_count,
        "posts": posts,
        "post_count": post_count,
        "creators": creators,
        "creator_count": creator_count,
        "premium_creator_count": premium_creator_count,
        "page_title": f"Search｜搜索 - {keyword}" if keyword else "Search｜搜索",
        "search_keyword": keyword,
        "main_title": "Search Result｜搜尋結果",
        "sub_title_1": "",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Search｜搜尋",
        "bread_crumb_3": "Search Result｜搜索結果",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/search",
        "bread_crumb_3_url": f"/search/?keyword={keyword}",
    }
    return render(request, 'pages/search_results.html', context)


def tag(request):
    context = {
        "page_title": "Tag", 
        "main_title": "與XXX相關的內容",
        "sub_title_1": "標籤",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "標籤",
        "bread_crumb_3": "XXX",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/tag",
        "bread_crumb_3_url": "/tag",
    }
    return render(request, 'pages/tag_results.html', context)


def archive(request):
    context = {
        "page_title": "存檔紀錄｜Archive", 
        "main_title": "存檔紀錄",
        "sub_title_1": "查詢過去的筆記記錄",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "存檔",
        "bread_crumb_3": "xx-xx-xx~xx-xx-xx",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/archive",
        "bread_crumb_3_url": "/archive",
    }
    return render(request, 'pages/archive_results.html', context)


def find_destined_work(request):
    # Retrieve inputs from the query string
    name = request.GET.get("name")
    dob = request.GET.get("dob")
    gender = request.GET.get("gender")
    blood = request.GET.get("blood")
    color = request.GET.get("color")
    
    painting_products = Product.objects.filter(category__category_name="Oil Painting | 油畫")

    soul_num = get_soul_number(dob)

    painting_products_scores = []

    for painting in painting_products:
        match_score = 0
        # check if dob matches created_at
        created_at = painting.created_date.strftime("%Y-%m-%d")
        created_at_soul_num = get_soul_number(created_at)
        if created_at_soul_num == soul_num: match_score += 9
        if gender == painting.gender: match_score += 3
        if blood == painting.blood: match_score +=  5
        if color == painting.color: match_score += 11

        painting_products_scores.append({painting.pk: match_score})

    # 1. Shuffle the list first to randomize items with the same values
    random.shuffle(painting_products_scores)

    # 2. Sort by the value (the first value in each dictionary) in descending order
    # list(d.values())[0] gets the value regardless of what the key is
    painting_products_scores.sort(key=lambda d: list(d.values())[0], reverse=True)
    product_pk = next(iter(painting_products_scores[0]))
    destined_work = Product.objects.filter(pk=product_pk)
    distined_work_json = {
        "product_name": destined_work[0].product_name,
        "product_description": destined_work[0].description,
        "product_image_url": str(destined_work[0].images.url),
        "product_url": destined_work[0].get_url(),
    }
    
    # Example logic to select a post
    destined_data = {
        'user_name': f'Random Result for {name}',
        'distined_work_json': distined_work_json,
    }
    
    return JsonResponse({'destined_data': destined_data})


def shipping_policy(request):
    return render(request, 'pages/shipping_policy.html', {})


def after_sales_service(request):
    return render(request, 'pages/after_sales_service.html', {})


def how_to_order(request):
    return render(request, 'pages/how_to_order.html', {})


def ip_policy(request):
    return render(request, 'pages/ip_policy.html', {})


def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html', {})


def faqs(request):
    return render(request, 'pages/faqs.html', {})


def member_policy(request):
    return render(request, 'pages/member_policy.html', {})