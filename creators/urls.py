from django.urls import path
from . import views

urlpatterns = [
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

    # Dashboard
    path('dashboard/', views.dashboard_overview, name='dashboard'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/<int:line_id>/dispatch/', views.dashboard_dispatch_line, name='dashboard_dispatch_line'),
    path('dashboard/profile/', views.dashboard_profile_edit, name='dashboard_profile'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/blog/', views.dashboard_blog_list, name='dashboard_blog'),
    path('dashboard/blog/new/', views.dashboard_blog_create, name='dashboard_blog_new'),
    path('dashboard/blog/<int:pk>/edit/', views.dashboard_blog_edit, name='dashboard_blog_edit'),

    # Catch-all LAST
    path('<slug:slug>/', views.artisan_detail, name='artisan_detail'),
]