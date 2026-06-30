class CaptureAnonymousSessionMiddleware:
    """
    save session key in the request object for retrieving upon login and merge cart data
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.prior_session_key = request.session.session_key
        return self.get_response(request)
    

class CurrencyMiddleware:
    """
    ensure user's preferred currency is available globally in every template without manual passing
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach the preferred currency to the request object (key, default)
        request.currency = request.COOKIES.get('user_currency', 'HKD')
        request.locked_at = request.session.get('locked_at')
        return self.get_response(request)
