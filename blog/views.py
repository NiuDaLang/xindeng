from django.shortcuts import render

# Create your views here.
def all_posts(request):
    context = {
        "main_title": "店主筆記",
        "sub_title": "生活的點點滴滴，就像星空點點，匯聚成燦爛的夜空",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "筆記",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
    }

    return render(request, 'pages/all_posts.html', context)


def post(request):
    context = {
        "main_title": "店主筆記 - 【文章主題】",
        "sub_title": "【文章副題】",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "筆記",
        "bread_crumb_3": "【文章主題】",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        "bread_crumb_3_url": "/blog/post",
    }

    return render(request, 'pages/post.html', context)