from django.shortcuts import render
from store.models import Product
from blog.models import Post
import random
from django.contrib.sites.shortcuts import get_current_site
from .utils import get_soul_number
from django.db.models import Q


def test(request):
    return render(request, 'pages/test.html')


def home(request):
    all_products = Product.products.all()
    product_ids = all_products.values_list('id', flat=True)
    random_ids = random.sample(list(product_ids), 6)
    featured_products = Product.products.filter(id__in=random_ids)

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


def error_404(request):
    return render(request, '404.html', {"page_title": "404"}, status=404, )


def error_500(request):
    return render(request, '500.html', {"page_title": "500"}, status=500)


def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.prefetch_related('variations', 'tags').select_related('category').filter(
                (
                    Q(product_name__icontains=keyword) |
                    Q(details__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(brand__icontains=keyword) |
                    Q(category__category_name__icontains=keyword) | 
                    Q(origin__icontains=keyword) |
                    Q(gender__icontains=keyword) |
                    Q(blood__icontains=keyword) |
                    Q(tags__name__icontains=keyword) |
                    Q(color__icontains=keyword) & 
                    Q(is_active=True)
                ),
                # The condition to ensure at least one variation exists
                variations__isnull=False
            ).distinct().order_by("-created_date")
            product_count = products.count()

            posts = Post.objects.order_by("-created_at").filter(
                Q(title__icontains=keyword) |
                Q(short_description__icontains=keyword) |
                Q(post_category__icontains=keyword) |
                Q(author__username__icontains=keyword) |
                Q(blog_body__icontains=keyword) |
                Q(tags__name__icontains=keyword) |
                Q(post_type__icontains=keyword) & 
                Q(status="Published")
            ).distinct()
            post_count = posts.count()

            total_count = product_count + post_count

    context = {
        "total_count": total_count,
        "products": products,
        "product_count": product_count,
        "posts": posts,
        "post_count": post_count,
        "page_title": f"Search｜搜索 - {keyword}",
        "search_keyword": keyword,
        "main_title": f"Search Result｜搜尋結果",
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


from django.http import JsonResponse

def find_destined_work(request):
    # Retrieve inputs from the query string
    name = request.GET.get("name")
    dob = request.GET.get("dob")
    gender = request.GET.get("gender")
    blood = request.GET.get("blood")
    color = request.GET.get("color")
    print("name:", name, "dob:", dob, "gender:", gender, "blood:", blood, "color:", color)
    
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

    # destined_work = Post.objects.filter(pk=int(painting_products_scores[0]))
    print("destined_work: ", destined_work)
    distined_work_json = {
        "product_name": destined_work[0].product_name,
        "product_description": destined_work[0].description,
        "product_image_url": str(destined_work[0].images.url),
        "product_url": destined_work[0].get_url(),
    }
    print("distined_work_json: ", distined_work_json)
    
    # Example logic to select a post
    destined_data = {
        'user_name': f'Random Result for {name}',
        'distined_work_json': distined_work_json,
    }
    
    return JsonResponse({'destined_data': destined_data})

