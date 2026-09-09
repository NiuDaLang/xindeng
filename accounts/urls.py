from django.urls import path, re_path
from . import views


urlpatterns = [
    path("register/", views.register, name="register"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),

    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("reset_password_validate/<uidb64>/<token>/", views.reset_password_validate, name="reset_password_validate"),
    path("reset_password/", views.reset_password, name="reset_password"),
    
    # dashboard
    path("dashboard/<str:subpage>/", views.dashboard, name="dashboard"),
    path("get_profile_strength/", views.get_profile_strength, name="get_profile_strength"),
    path('check-username/', views.check_username, name='check_username'),

    # dashboard - addresses
    path("edit_address/<pk>/", views.edit_address, name="edit_address"),
    path("update_address/<pk>/", views.update_address, name="update_address"),
    path("create_address/", views.create_address, name="create_address"),
    path("delete_address/<pk>/", views.delete_address, name="delete_address"),
    path("set_default_address/<pk>/", views.set_default_address, name="set_default_address"),

    # dashboard - wishlist & favorites
    path("check_stock/<int:variation_id>/", views.check_stock, name="check_stock"),

    path("add_to_cart_qty/<int:variation_id>/<str:source>/", views.add_to_cart_qty, name="add_to_cart_qty"),
    path("add_to_cart_from_dashboard/<int:variation_id>/", views.add_to_cart_from_dashboard, name="add_to_cart_from_dashboard"),
    path("get_wishlist_item/<int:item_id>/", views.get_wishlist_item, name="get_wishlist_item"),
    path("delete_favorite_item/<int:item_id>/", views.delete_favorite_item, name="delete_favorite_item"),

    # dashboard - help
    path('api/conversation/<int:member_id>/', views.api_conversation, name='api_conversation'),
    path('api/search_messages/', views.api_search_messages, name='api_search_messages'),
    path('api/send_message/', views.send_message, name='api_send_message'),
    path('api/my_conversation/', views.api_my_conversation, name='api_my_conversation'),
    path('api/mark_all_read/', views.api_mark_all_read, name='api_mark_all_read'),
    path('api/get_all_unread_counts/', views.api_get_all_unread_counts, name='api_get_all_unread_counts'),

    # Unread count (used by HTMX badges)
    path('get_unread_count/', views.get_unread_count, name='get_unread_count'),
    path('get_unread_count/<int:sender_id>/', views.get_unread_count, name='get_unread_count_member'),
    
    # Mark as read
    path('mark_read/<int:msg_id>', views.mark_read, name='mark_read'),



    # dashboard - threed
    path("dashboard/threed/firework", views.firework, name="firework"),

    path("vouchers/claim/<str:voucher_id>/", views.claim_voucher_routing_view, name="claim_voucher_url"),



] 
