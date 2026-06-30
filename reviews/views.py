from django.shortcuts import render
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from store.models import Product
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentImage
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from orders.models import OrderProduct
from django.core.exceptions import FieldError


def check_user_has_purchased_product(user, product_id):
    """
    Queries past transaction tables using your exact Order schemas:
    Checks if order__is_ordered=True and matches fulfillment status targets.
    """
    if not user or not user.is_authenticated:
        return False
    try:
        return OrderProduct.objects.filter(
            user=user,
            product_id=product_id,
            order__is_ordered=True,
            order__order_status__in=['Delivered', 'All_Dispatched', 'Partly_Dispatched', 'Processing']
        ).exists()
    except Exception:
        return False
        

@login_required
@require_POST
def submit_review_htmx(request, product_id=None):
    """
    Polymorphic endpoint: Automatically detects whether it is processing an 
    e-commerce purchase verification or a generic blog post comment request.
    """
    incoming_content_type_id = request.POST.get("content_type")
    incoming_object_id = request.POST.get("object_id")

    review_text = request.POST.get("comment", "").strip()
    raw_rating = request.POST.get("rating")
    
    target_content_type = None
    target_object_id = None
    parsed_rating = None

    if incoming_content_type_id and incoming_object_id:
        # -------------------------------------------------------------
        # BRANCH A: PATHWAY FOR GENERIC BLOG POST COMMENTS
        # -------------------------------------------------------------
        target_content_type = get_object_or_404(ContentType, id=int(incoming_content_type_id))
        target_object_id = int(incoming_object_id)
        parsed_rating = None # Discussion boards explicitly bypass star calculations
    else:
        # -------------------------------------------------------------
        # BRANCH B: PATHWAY FOR VERIFIED E-COMMERCE PRODUCT REVIEWS
        # -------------------------------------------------------------
        from store.models import Product
        actual_product_id = product_id or request.POST.get("product_id")
        product_obj = get_object_or_404(Product, id=int(actual_product_id))
        
        if not check_user_has_purchased_product(request.user, product_obj.id):
            return HttpResponseForbidden("您需要先購買此商品才能提交評價。 | Purchase required.")

        target_content_type = ContentType.objects.get_for_model(product_obj)
        target_object_id = product_obj.id
        
        # Enforce an absolute cap of exactly 1 unique store feedback submission per buyer profile
        existing_review = Comment.objects.filter(
            user=request.user, 
            content_type=target_content_type, 
            object_id=target_object_id
        ).exists()
        
        if existing_review:
            return HttpResponse("您已對此商品提交過評價。 | Review already exists.", status=400)

        try:
            parsed_rating = float(raw_rating) if raw_rating else 5.0
        except ValueError:
            parsed_rating = 5.0

    # Capture the visitor's relative remote network location address footprint safely
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR', '')

    new_comment = Comment.objects.create(
        content_type=target_content_type,
        object_id=target_object_id,
        user=request.user,
        text=review_text,
        rating=parsed_rating,
        ip=client_ip,
        is_approved=True
    )

    # Process up to 5 optional uploaded file attachment pictures safely
    uploaded_files = request.FILES.getlist("review_images")
    for file in uploaded_files[:5]:
        CommentImage.objects.create(comment=new_comment, image=file)

    context = {"review": new_comment, "request": request}
    review_card_html = render_to_string('store/includes/review_card.html', context, request=request)
    
    # 🌟 CLEAN RESET PAYLOAD: Swaps an empty string back over the input form elements upon success
    oob_clear_form = '<form id="comment-submission-form" hx-swap-oob="true" class="hidden"></form>'
    return HttpResponse(review_card_html + oob_clear_form)


@login_required
@require_http_methods(["GET", "POST"])
def edit_review_htmx(request, review_id):
    """
    Surgically injects update forms into daisyUI modals,
    handling modifications smoothly via standard async sweeps.
    """
    review_obj = get_object_or_404(Comment, id=review_id, user=request.user)
    
    if request.method == "POST":
        review_obj.text = request.POST.get("comment", "").strip()
        if request.POST.get("rating"):
            review_obj.rating = float(request.POST.get("rating"))
        review_obj.save()
        
        # Process extra image slots if space allows (Max 5 items total)
        uploaded_files = request.FILES.getlist("review_images")
        current_count = review_obj.images.count()
        remaining_slots = max(0, 5 - current_count)
        
        for file in uploaded_files[:remaining_slots]:
            CommentImage.objects.create(comment=review_obj, image=file)
            
        context = {"review": review_obj, "request": request}
        updated_card_html = render_to_string('store/partials/review_card.html', context, request=request)
        
        oob_close_modal = '<script>document.getElementById("global-review-modal").removeAttribute("open");</script>'
        return HttpResponse(updated_card_html + oob_close_modal)

    context = {"review": review_obj}
    modal_content_html = render_to_string('store/partials/edit_review_form.html', context, request=request)
    return HttpResponse(modal_content_html)


@login_required
@require_http_methods(["DELETE"])
def delete_review_htmx(request, review_id):
    review_obj = get_object_or_404(Comment, id=review_id, user=request.user)
    review_obj.delete()
    return HttpResponse("")
