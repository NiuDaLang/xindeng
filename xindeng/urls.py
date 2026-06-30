"""
URL configuration for xindeng project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404, handler500

# Map global system error loops directly to your root views namespace strings
handler404 = 'xindeng.views.error_404'
handler500 = 'xindeng.views.error_500'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # apps
    path("blog/", include('blog.urls')),
    path("accounts/", include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path("carts/", include('carts.urls')),
    path("orders/", include('orders.urls')),
    path("store/", include('store.urls')),
    path('reviews/', include('reviews.urls')), 
    # pages
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("collaboration/", views.collaboration, name="collaboration"),
    path("search/", views.search, name="search"),
    path("tag/", views.tag, name="tag"),
    path("archive/", views.archive, name="archive"),

    # utils
    path("find_destined_work", views.find_destined_work, name="find_destined_work"),

    # footer
    path("shipping_policy/", views.shipping_policy, name="shipping_policy"),
    path("after_sales_service/", views.after_sales_service, name="after_sales_service"),
    path("how_to_order/", views.how_to_order, name="how_to_order"),
    path("ip_policy/", views.ip_policy, name="ip_policy"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path("member_policy/", views.member_policy, name="member_policy"),
    path("faqs/", views.faqs, name="faqs"),


    # errors
    path("error/404/", views.error_404, name="error_404"),
    path("error/500/", views.error_500, name="error_500"),

    path("test/", views.test, name="test")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
