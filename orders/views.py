from django.shortcuts import render

# Create your views here.
def place_order(request):
    context = {
        "main_title": "支 付 訂 單",
        "sub_title": "迎接寶貝",
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "寶貝們",
        "bread_crumb_3": "訂單支付",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products",
        "bread_crumb_3_url": "/orders/place_order",
    }
    return render(request, 'orders/place_order.html', context)