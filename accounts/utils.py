import datetime
from borax.calendars.lunardate import LunarDate
from .data import SOLAR
from django.shortcuts import render
import json
from django.http import HttpResponse


def check_today_is_solar_term(today):
    lunar_today = LunarDate.from_solar_date(today.year, today.month, today.day)
    term_name = lunar_today.term

    if term_name:
        return term_name
    else:
        return None


def get_next_solar_term(current_key):
    # Convert keys to a list to access by index
    keys = list(SOLAR.keys())
    
    # Find the index of the current key
    current_index = keys.index(current_key)
    
    # Calculate next index (modulo ensures wrap-around to 0)
    next_index = (current_index + 1) % len(keys)
    
    next_key = keys[next_index]
    next_value = SOLAR[next_key]
    
    return next_key, next_value


def get_current_solar_term_period(target_date):
    # Iterate backwards (up to 20 days) to find the most recent term start
    for i in range(21):
        check_date = target_date - datetime.timedelta(days=i)
        ld = LunarDate.from_solar_date(check_date.year, check_date.month, check_date.day)
        
        # .term is only non-None on the start day of a solar term
        term = ld.term
        if term:
            return term, check_date
    return None, None


def htmx_unavailable_response(request, title, text, icon="error"):
    response = HttpResponse(status=204)
    response['HX-Trigger'] = json.dumps({
        "errorMssg": {  # Ensure this matches your JS event listener
            "title": title,
            "html": text,
            "icon": icon
        }
    })
    return response
