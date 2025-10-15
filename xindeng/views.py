from django.shortcuts import render


def home(request):
    
    return render(request, 'home.html', )


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