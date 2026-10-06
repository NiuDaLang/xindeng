# store/urls.py
from django.urls import path, re_path
from . import views


urlpatterns = [
    path("products/<str:category_slug>", views.products, name="products"),
    path("product/<slug:category_slug>/<slug:product_slug>/", views.product, name="product"),
    re_path(
        r"^product/(?P<category_slug>[-\w]+)/(?P<product_slug>[-\w]+)/$",
        views.product,
        name="product",
    ),

    path("products/filter_products/", views.filter_products, name="filter_products"),
    path('digital/download/<uuid:token_id>/', views.secure_file_download_gate, name='secure_file_download_gate'),

    # Superuser review actions
    path("review/product/<int:product_id>/approve/", views.review_product_approve, name="review_product_approve"),
    path("review/product/<int:product_id>/reject/",  views.review_product_reject,  name="review_product_reject"),
]
