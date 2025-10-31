from django.shortcuts import render


def test(request):
    return render(request, 'pages/test.html')


def home(request):
    
    return render(request, 'home.html', )


def about(request):
    context = {
        "main_title": "關 於 我 們",
        "sub_title": "關於品牌/作者/店主的故事",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "關 於 我 們",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/about",
    }
    return render(request, 'pages/about.html', context)


def collaboration(request):
    context = {
        "main_title": "與 我 們 合 作",
        "sub_title": "共同探討能量的凝聚",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "與 我 們 合 作",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/collaboration",
    }
    return render(request, 'pages/collaboration.html', context)


def contact(request):
    context = {
        "main_title": "聯 繫 我 們",
        "sub_title": "應物空三世 隨緣遍十方",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "聯繫我們",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/contact",
        "bread_crumb_3_url": "",
    }
    return render(request, 'pages/contact.html', context)


def error_404(request):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


def search(request):
    context = {
        "main_title": "XXX的搜尋結果",
        "sub_title": "搜尋",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "搜尋",
        "bread_crumb_3": "XXX",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/search",
        "bread_crumb_3_url": "/search",
    }
    return render(request, 'pages/search_results.html', context)


def tag(request):
    context = {
        "main_title": "與XXX相關的內容",
        "sub_title": "標籤",
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
        "main_title": "存檔紀錄",
        "sub_title": "查詢過去的筆記記錄",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "存檔",
        "bread_crumb_3": "xx-xx-xx~xx-xx-xx",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/archive",
        "bread_crumb_3_url": "/archive",
    }
    return render(request, 'pages/archive_results.html', context)
