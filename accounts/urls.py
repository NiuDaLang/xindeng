from django.urls import path
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

    # dashboard - wishlist & favorites
    path("check_stock/<int:variation_id>/", views.check_stock, name="check_stock"),

    path("add_to_cart_qty/<int:variation_id>/<str:source>/", views.add_to_cart_qty, name="add_to_cart_qty"),
    path("add_to_cart_from_dashboard/<int:variation_id>/", views.add_to_cart_from_dashboard, name="add_to_cart_from_dashboard"),
    path("get_wishlist_item/<int:item_id>/", views.get_wishlist_item, name="get_wishlist_item"),
    path("delete_favorite_item/<int:item_id>/", views.delete_favorite_item, name="delete_favorite_item"),

    # dashboard - help
    path("send_message/", views.send_message, name="send_message"),
    path("refresh_chat/", views.refresh_chat, name="refresh_chat"),
    path("filter_message_by_member/<int:member_id>", views.filter_message_by_member, name="filter_message_by_member"),
    path("mark_read/<int:msg_id>", views.mark_read, name="mark_read"),
    path("load_earlier_messages/", views.load_earlier_messages, name="load_earlier_messages"),
    path("get_unread_count/", views.get_unread_count, name="get_unread_count"),
    path("get_unread_count/<int:sender_id>", views.get_unread_count, name="get_unread_count"),




    path("edit_order/", views.edit_order, name="edit_order"),
    path("help/", views.help, name="help"),

    # path("dashboard/threed/firework", views.firework, name="firework"),

    # path("claim_voucher_url/<uuid>/", views.claim_voucher_url, "claim_voucher_url")
] 
