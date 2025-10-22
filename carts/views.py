from django.shortcuts import render

# Create your views here.
def cart(request):
    context = {
        "main_title": "購物車",
        "sub_title": "此處有驚喜在等待您",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "購物車",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/carts/cart",
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    context = {
        "main_title": "訂單訊息",
        "sub_title": "寶貝們期待著早日與您會面！",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "訂單訊息",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/carts/checkout",
    }
    return render(request, 'store/checkout.html', context)