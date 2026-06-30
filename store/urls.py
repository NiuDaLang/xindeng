from django.urls import path
from . import views


urlpatterns = [
    path("products/<str:category_slug>", views.products, name="products"),
    path("product/<slug:category_slug>/<slug:product_slug>/", views.product, name="product"),
    path("products/filter_products/", views.filter_products, name="filter_products"),
    path('digital/download/<uuid:token_id>/', views.secure_file_download_gate, name='secure_file_download_gate'),
]
