from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/member_profile/", views.member_profile, name="member_profile"),
    path("dashboard/addresses/", views.addresses, name="addresses"),
    path("dashboard/orders/", views.orders, name="orders"),
    path("dashboard/orders/order", views.order, name="order"),
    path("dashboard/help/", views.help, name="help"),

] 