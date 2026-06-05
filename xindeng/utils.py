import os

# from iplocate import IPLocateClient

# def get_country(ip_address):
#     client = IPLocateClient(api_key=os.environ.get("IPLOCATE_API_KEY"))
#     result = client.lookup(ip_address)
#     return result.country


def get_soul_number(date_string):
    # 1. Extract only the digits from the string
    digits = [int(char) for char in date_string if char.isdigit()]
    current_sum = sum(digits)
    
    # 2. Keep summing until we reach a single digit
    while current_sum >= 10:
        # Convert the current sum to a list of its own digits
        current_sum = sum(int(d) for d in str(current_sum))
        
    return current_sum