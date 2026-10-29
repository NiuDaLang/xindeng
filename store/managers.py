# store/managers.py
from django.db import models
from django.db.models import Exists, OuterRef, Min, Q

class ProductManager(models.Manager):

    def all_available(self, variation_model):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(Exists(variation_model.objects.filter(product=OuterRef('pk'), is_available=True))).distinct().order_by('product_name')
    
    def all_available_with_stock(self):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(variations__stock__gt=0).distinct().order_by('product_name')
    
    def available_by_category(self, category_slug, variation_model):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(category__slug=category_slug).filter(Exists(variation_model.objects.filter(product=OuterRef('pk'),is_available=True))).distinct().order_by('product_name')
    
    def available_by_category_with_stock(self, category_slug):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(category__slug=category_slug).filter(variations__is_available=True, variations__stock__gt=0).distinct().order_by('product_name')
    
    def available_by_category_format(self, category_slug):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(category__product_format=category_slug, variations__is_available=True).distinct().order_by('product_name')

    def available_by_category_format_with_stock(self, category_slug):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(category__product_format=category_slug, variations__is_available=True, variations__stock__gt=0).distinct().order_by('product_name')
    
    def available_by_color(self, color):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(color=color).distinct().order_by('product_name')
    
    def available_with_tags(self, tags_ids):
        return self.filter(is_active=True, is_deleted=False, status="Published").filter(tags__id__in=tags_ids).distinct().order_by('product_name')

    def lowest_prices(self, products):
        """
        Annotates `lowest_price` onto an ALREADY-FILTERED queryset.

        Operates on the queryset passed in; does not build its own
        query. The status / is_active / is_deleted constraints are the
        caller's responsibility (typically one of the available_by_*
        methods above). Do NOT add a status filter here — the input is
        already constrained, and adding a second filter would encode
        the same constraint in two places and let them drift.
        """
        lowest_prices = {}
        for product in products:
            variations = product.variations.filter(is_available=True)
            prices = []
            for variation in variations:
                prices.append(variation.price)
            lowest_price = min(prices)
            lowest_prices[product.pk] = lowest_price
            product.lowest_price = lowest_prices[product.pk]
        
        return products

    def available_within_price_range(self, price):
        price_range_products = self.annotate(
            min_price=Min(
                'variations__price', 
                filter=Q(variations__is_available=True)
            )
        ).filter(min_price__lte=price).filter(is_active=True, is_deleted=False, status="Published").distinct()
        return price_range_products