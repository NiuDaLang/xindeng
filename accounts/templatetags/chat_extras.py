# accounts/templatetags/chat_extras.py
import re
from django import template
from django.utils.safestring import mark_safe
from django.core.cache import cache

register = template.Library()

@register.filter
def format_chat(text):
    if not text:
        return ""
    
    from django.utils.html import escape
    text = escape(text)
    
    url_pattern = re.compile(r'(https?://[^\s]+)')

    def replace_with_link(match):
        url = match.group(0)
        
        if "/product/" in url:
            product_info = get_product_info_from_url(url)
            
            if product_info:
                return f'''
                <a href="{url}" target="_blank" class="product-link-card">
                    <div class="product-link-content">
                        <img src="{product_info['image_url']}" alt="{product_info['name']}" class="product-link-image" loading="lazy">
                        <div class="product-link-details">
                            <span class="product-link-name">{product_info['name']}</span>
                            <span class="product-link-btn">
                                <i class="fa-solid fa-eye"></i>
                                <span>View Product</span>
                                <span class="product-link-btn-cn">｜查看產品</span>
                            </span>
                        </div>
                    </div>
                </a>
                '''
            else:
                return f'<a href="{url}" target="_blank" class="btn btn-xs btn-outline btn-primary">View Product｜查看產品 📦</a>'
        
        return f'<a href="{url}" target="_blank" class="link link-primary">{url}</a>'
    
    processed_text = url_pattern.sub(replace_with_link, text)
    return mark_safe(processed_text)


def get_product_info_from_url(url):
    """Extract product info from URL with caching"""
    product_info = None  # ✅ Initialize variable
    
    try:
        # Check cache first
        cache_key = f'product_info_{url}'
        cached_info = cache.get(cache_key)
        if cached_info:
            return cached_info
        
        from store.models import Product  # Adjust import based on your app structure
        
        # Parse URL to get product slug
        # Expected format: /store/product/<category_slug>/<product_slug>/
        import urllib.parse
        path = urllib.parse.urlparse(url).path
        parts = [p for p in path.split('/') if p]
        
        # Find 'product' in path and get the slug after it
        if 'product' in parts:
            product_index = parts.index('product')
            if product_index + 2 < len(parts):
                product_slug = parts[product_index + 2]  # Skip category_slug
                
                # Get product from database
                product = Product.objects.filter(slug=product_slug, is_active=True).first()
                
                if product:
                    product_info = {
                        'name': product.product_name,
                        'image_url': product.images.url if product.images else '/static/images/default-product.png',
                    }
                    
                    # Cache for 1 hour
                    cache.set(cache_key, product_info, 3600)
    
    except Exception as e:
        print(f"Error extracting product info: {e}")
        product_info = None
    
    return product_info