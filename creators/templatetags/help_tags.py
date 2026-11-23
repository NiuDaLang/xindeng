# creators/templatetags/help_tags.py
from django import template
from creators.help_content import HELP_TOPICS

register = template.Library()

@register.inclusion_tag('artisans/dashboard/partials/_help_button.html')
def help_button(topic):
    content = HELP_TOPICS.get(topic, {})
    return {
        'topic': topic,
        'title': content.get('title', ''),
        'body': content.get('body', ''),
    }