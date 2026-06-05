import datetime
from celery import shared_task
from .utils import get_current_solar_term_period
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import opencc
from .data import SOLAR


def get_solar_term():
    today = datetime.date.today()
    current_term, start_date = get_current_solar_term_period(today)
    term_en = SOLAR[current_term]
    trad_term = None
    if current_term:
        translator = opencc.OpenCC('s2t.json')
        trad_term = translator.convert(current_term)
    return trad_term, term_en

@shared_task
def update_solar_term_broadcast():
    term, term_en = get_solar_term()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "solar_updates", 
        {"type": "solar_message", "term": term, "term_en": term_en}
    )
