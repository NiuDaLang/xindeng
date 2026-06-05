from django.db import models
from django.db.models import Exists, OuterRef, Min, Q

class ProductManager(models.Manager):

    def all_available(self, variation_model):
        return self.filter(is_active=True).filter(Exists(variation_model.objects.filter(product=OuterRef('pk'), is_available=True))).distinct().order_by('product_name')
    
    def all_available_with_stock(self):
        return self.filter(is_active=True).filter(variations__stock__gt=0).distinct().order_by('product_name')
    
    def available_by_category(self, category_slug, variation_model):
        return self.filter(is_active=True).filter(category__slug=category_slug).filter(Exists(variation_model.objects.filter(product=OuterRef('pk'),is_available=True))).distinct().order_by('product_name')
    
    def available_by_category_with_stock(self, category_slug):
        return self.filter(is_active=True).filter(category__slug=category_slug).filter(variations__is_available=True, variations__stock__gt=0).distinct().order_by('product_name')
    
    def available_by_category_format(self, category_slug):
        return self.filter(is_active=True).filter(category__product_format=category_slug, variations__is_available=True).distinct().order_by('product_name')

    def available_by_category_format_with_stock(self, category_slug):
        return self.filter(is_active=True).filter(category__product_format=category_slug, variations__is_available=True, variations__stock__gt=0).distinct().order_by('product_name')
    
    def available_by_color(self, color):
        return self.filter(is_active=True).filter(color=color).distinct().order_by('product_name')
    
    def available_with_tags(self, tags_ids):
        return self.filter(is_active=True).filter(tags__id__in=tags_ids).distinct().order_by('product_name')

    def lowest_prices(self, products):
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
        ).filter(min_price__lte=price).filter(is_active=True).distinct()
        return price_range_products