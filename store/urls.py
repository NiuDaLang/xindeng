from django.urls import path
from . import views


urlpatterns = [
    path("products/", views.products, name="products"),
    path("products/product/", views.product, name="product"),
    path("cart/", views.cart, name="cart"),
]
