from django.urls import path
from . import views


urlpatterns = [
    # Asynchronous HTMX processing endpoint rules
    path('htmx/submit-review/<int:product_id>/', views.submit_review_htmx, name='submit_review_htmx'),
    path('htmx/edit-review/<int:review_id>/', views.edit_review_htmx, name='edit_review_htmx'),
    path('htmx/delete-review/<int:review_id>/', views.delete_review_htmx, name='delete_review_htmx'),
]