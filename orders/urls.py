from django.urls import path
from . import views
from . import paypal
from . import utils


urlpatterns = [
    path("place_order/<str:proforma_invoice_no>/", views.place_order, name="place_order"),
    path("order_complete/", views.order_complete, name="order_complete"),
    path('order/download/invoice/<str:order_id>/', views.download_invoice_pdf_view, name='generate_order_confirmation_pdf'),
    path('order/guest_order_verify/', views.guest_order_verify, name='guest_order_verify'),

    path('cancel_request/<str:order_number>/', views.process_order_cancellation, name='cancel'),

    # paypal
    path('api/paypal/token/', paypal.get_paypal_client_token, name='paypal_token'),
    path("api/paypal/create_paypal_order/", paypal.create_paypal_order, name="create_paypal_order"),
    path("api/paypal/capture_paypal_order/", paypal.capture_paypal_order, name="capture_paypal_order"),
    path('api/voucher/complete_order/', views.complete_zero_due_voucher_order, name='complete_zero_due_voucher_order'),
    # path("paypal/execute/", paypal.execute, name="paypal_execute"),
    # path("paypal/cancel/", paypal.cancel, name="paypal_cancel")

]
