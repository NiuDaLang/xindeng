import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def format_chat(text):
    if not text:
        return ""
    
    url_pattern = re.compile(r'(https?://[^\s]+)')

    def replace_with_link(match):
        url = match.group(0)
        # check if it's a product link
        if "/product/" in url:
            return f'''
                <a href="{url}" target="_blank" class="btn btn-xs btn-outline btn-primary">View Product｜查看產品 📦</a>
            '''
        # standard link for other URLs
        return f'<a href="{url}" target="_blank" class="link link-primary">{url}</a>'
    
    processed_text = url_pattern.sub(replace_with_link, text)
    return mark_safe(processed_text)
    