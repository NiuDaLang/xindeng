from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart
from .views import _cart_id


@receiver(user_logged_in)
def merge_anonymous_cart_on_login(sender, user, request, **kwargs):
    # 1. Get the session key used before logging in
    anonymous_session_key = getattr(request, "prior_session_key", None)

    if anonymous_session_key:
        try:
            # 2. Retrieve the anonymous cart associated with the session key
            anonymous_cart = Cart.objects.filter(cart_id=anonymous_session_key).first()

            if anonymous_cart:
                # 3. Retrieve the authenticated user's cart
                authenticated_cart = Cart.objects.filter(user=user)
                if authenticated_cart.exists():
                    authenticated_cart = authenticated_cart.first()
                else:
                    authenticated_cart = Cart.objects.create(cart_id=_cart_id(request), user=user)

                # 4. Merge the anonymous cart items into the authenticated cart
                for item in anonymous_cart.cartitem_set.all():
                    # Check if the item already exists in the authenticated cart
                    existing_item = authenticated_cart.cartitem_set.filter(product_variation=item.product_variation).first()

                    if existing_item:
                        # If the item exists, update the quantity
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        # If the item doesn't exist, create a new cart item
                        item.cart = authenticated_cart
                        item.save()

                # 5. Delete the anonymous cart
                anonymous_cart.delete()
        except Cart.DoesNotExist:
            pass
