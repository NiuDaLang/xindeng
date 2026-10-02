# creators/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_overview, name='a_dashboard'),
    path('dashboard/orders/', views.dashboard_orders, name='a_dashboard_orders'),
    path('dashboard/orders/<int:line_id>/dispatch/', views.dashboard_dispatch_line, name='a_dashboard_dispatch_line'),
    path('dashboard/blog/', views.dashboard_blog_list, name='a_dashboard_blog'),
    path('dashboard/blog/new/', views.dashboard_blog_create, name='a_dashboard_blog_new'),
    path('dashboard/blog/<int:pk>/edit/', views.dashboard_blog_edit, name='a_dashboard_blog_edit'),
    path('dashboard/blog/<int:pk>/submit/', views.dashboard_blog_submit, name='a_dashboard_blog_submit'),
    path('dashboard/blog/<int:pk>/withdraw/', views.dashboard_blog_withdraw, name='a_dashboard_blog_withdraw'),
    path('dashboard/blog/<int:pk>/delete/', views.dashboard_blog_delete, name='a_dashboard_blog_delete'),
    path('dashboard/blog/bulk-delete-drafts/', views.dashboard_blog_bulk_delete_drafts, name='a_dashboard_blog_bulk_delete_drafts'),
    
    path('dashboard/products/', views.dashboard_products_list, name='a_dashboard_products'),

    path('dashboard/products/new/', views.dashboard_product_create, name='a_dashboard_product_new'),
    path('dashboard/products/<int:pk>/edit/', views.dashboard_product_edit, name='a_dashboard_product_edit'),
    path('dashboard/products/<int:pk>/submit/', views.dashboard_product_submit, name='a_dashboard_product_submit'),
    path('dashboard/products/<int:pk>/withdraw/', views.dashboard_product_withdraw, name='a_dashboard_product_withdraw'),
    path('dashboard/products/<int:pk>/variations/add/', views.dashboard_product_variation_add, name='a_dashboard_product_variation_add'),
    path('dashboard/products/<int:pk>/variations/<int:variation_pk>/remove/', views.dashboard_product_variation_remove, name='a_dashboard_product_variation_remove'),
    path('dashboard/products/<int:pk>/variations/<int:variation_pk>/edit/', views.dashboard_product_variation_edit, name='a_dashboard_product_variation_edit'),
    path('dashboard/products/<int:pk>/delete/', views.dashboard_product_delete, name='a_dashboard_product_delete'),
    path('dashboard/products/<int:pk>/stock/', views.dashboard_product_stock_edit, name='a_dashboard_product_stock_edit'),
    path('dashboard/products/<int:pk>/request-deactivation/', views.dashboard_product_request_deactivation, name='a_dashboard_product_request_deactivation'),
    path('dashboard/products/<int:pk>/gallery/<int:gallery_pk>/delete/', views.dashboard_product_gallery_delete, name='a_dashboard_product_gallery_delete'),
    
    path('dashboard/profile/', views.dashboard_profile_edit, name='a_dashboard_profile'),
    path('dashboard/messages/', views.dashboard_messages, name='a_dashboard_messages'),

    # Public
    path('', views.artisan_landing, name='artisan_landing'),
    path('profiles/', views.artisan_list, name='artisan_list'),
    path('gallery/', views.artisan_gallery, name='artisan_gallery'),
    path('join/', views.artisan_join, name='artisan_join'),
    path('join/success/', views.artisan_join_success, name='artisan_join_success'),
    path('join/application_pdf/', views.artisan_join_pdf, name='artisan_join_pdf'),    
    path('blogs/', views.artisan_blog_list, name='artisan_blog_list'),

    # Role switch
    path('role-select/', views.role_select, name='role_select'),
    path('role/set/<str:role>/', views.set_role, name='set_role'),

    # Catch-all LAST
    path('<slug:slug>/', views.artisan_detail, name='artisan_detail'),
]