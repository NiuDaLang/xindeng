from django.shortcuts import render

# Create your views here.
def products(request):
    context = {
        "main_title": "寶貝們",
        "sub_title": "海闊天空 尋覓您的摯愛",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "寶貝們",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products",
    }
    return render(request,'store/products.html', context)


def product(request):
    context = {
        "main_title": "寶 貝 詳 情",
        "sub_title": "梅須遜雪三分白 雪卻輸梅一段香",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "寶貝們",
        "bread_crumb_3": "寶貝名",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products",
        "bread_crumb_3_url": "/",
    }
    return render(request, 'store/product.html', context)

