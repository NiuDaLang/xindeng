from django.urls import path
from . import views
from . import paypal
from . import utils


urlpatterns = [
    path("place_order/<str:proforma_invoice_no>/", views.place_order, name="place_order"),
    path("order_complete/", views.order_complete, name="order_complete"),
    # path("order_confirmation_pdf/<str:order_id>", views.order_confirmation_pdf, name="order_confirmation_pdf"),
    path("view_order_pdf/<str:order_id>", views.view_order_pdf, name="view_order_pdf"),

    # paypal
    path('api/paypal/token/', paypal.get_paypal_client_token, name='paypal_token'),
    path("api/paypal/create_paypal_order/", paypal.create_paypal_order, name="create_paypal_order"),
    path("api/paypal/capture_paypal_order/", paypal.capture_paypal_order, name="capture_paypal_order"),
    path("api/paypal/paypal_order_success/", paypal.paypal_order_success, name="paypal_order_success"),
    # path("paypal/execute/", paypal.execute, name="paypal_execute"),
    # path("paypal/cancel/", paypal.cancel, name="paypal_cancel")

]
