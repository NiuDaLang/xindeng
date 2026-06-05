from decimal import Decimal

def calculate_australia_tax(taxable_value_cny, exchange_rate):
    """
    Calculates Tax and Duty for Australia.
    taxable_value_cny: Total value of physical products in CNY
    exchange_rate: CNY to AUD rate
    """
    # 1. Convert to AUD to check thresholds
    value_aud = taxable_value_cny * Decimal(exchange_rate)
    
    tax_rate = Decimal('0.10')  # 10% GST
    duty_rate = Decimal('0.05') # Typical 5% Duty for artwork/goods
    
    gst_amount_cny = Decimal('0.00')
    duty_amount_cny = Decimal('0.00')

    # 2. Logic: Low Value vs High Value
    if value_aud > 1000:
        # High Value: Duty + GST are usually paid at the border by recipient.
        # You can choose to 'Estimate' it for the user here or mark as 'Paid at Border'.
        duty_amount_cny = taxable_value_cny * duty_rate
        # GST is calculated on (Value + Duty + Shipping)
        gst_amount_cny = (taxable_value_cny + duty_amount_cny) * tax_rate
    else:
        # Low Value: Duty is 0. 
        # GST is 10% if you are registered (turnover > $75k).
        gst_amount_cny = taxable_value_cny * tax_rate
        duty_amount_cny = Decimal('0.00')

    return gst_amount_cny, duty_amount_cny

# For Australia, the primary tax concern is the Goods and Services Tax (GST), which is 10%. 
# Unlike many other regions, Australia has removed the GST exemption for "low-value" imports; 
# consequently, GST applies to nearly all taxable goods regardless of their value.

# Australia Tax Logic Overview
# When a shipment is dispatched from Mainland China to Australia, the following rules apply:

# De Minimis Threshold (Customs Duty): $1,000 AUD.
#     Value ≤ $1,000 AUD: Generally no customs duty or border charges.
#     Value > $1,000 AUD: Subject to customs duty (typically 5%) and formal import processing fees at the border.

# GST (10%): If your annual turnover from Australian sales exceeds $75,000 AUD, 
# you are legally required to register with the Australian Taxation Office (ATO) and collect 10% GST at the point of sale for goods valued at $1,000 AUD or less.

# Digital Products: GST also applies to digital/e-products sold to Australian consumers. 
# Since your requirement is to exclude e-products from customs duty calculation, 
# you will only apply the logic below to your has_physical_items.

# Python Backend Implementation
# You can integrate this logic into a specialized function called by your calculate_tax_duty_api.

# GST Registration: If your store's total Australian sales are under the $75,000 AUD threshold, 
# you are not required to charge GST at checkout for low-value goods ($1,000 AUD or less). 
# In this case, your gst_amount_cny for low-value orders should be 0.00.

# Shipping & Insurance: Note that for high-value imports (> $1,000 AUD), 
# Australian GST is calculated on the "Taxable Importation" value, which includes the Customs Value + Duty + Shipping + Insurance.

def calculate_new_zealand_tax(taxable_value_cny, exchange_rate, is_gst_registered=True):
    """
    taxable_value_cny: Value of physical products in CNY
    exchange_rate: CNY to NZD rate
    is_gst_registered: Whether your shop is registered for NZ GST (>$60k turnover)
    """
    value_nzd = taxable_value_cny * Decimal(exchange_rate)
    gst_rate = Decimal('0.15')
    
    gst_amount_cny = Decimal('0.00')
    duty_amount_cny = Decimal('0.00')
    levy_amount_cny = Decimal('0.00')

    # 1. Low Value Processing (<= $1000 NZD)
    if value_nzd <= 1000:
        if is_gst_registered:
            gst_amount_cny = taxable_value_cny * gst_rate
            # 2026 Low-Value Goods Levy ($2.21 NZD + 15% GST)
            levy_nzd = Decimal('2.21') * Decimal('1.15')
            levy_amount_cny = levy_nzd / Decimal(exchange_rate)
    
    # 2. High Value Processing (> $1000 NZD)
    else:
        # Duty is typically 0% for original artwork. 
        # GST is often paid at border, but you can estimate it:
        gst_amount_cny = taxable_value_cny * gst_rate
        # Formal entry fees apply at border (> $1000 NZD)
        
    return gst_amount_cny, duty_amount_cny, levy_amount_cny


# For New Zealand, the tax logic centers on the 15% Goods and Services Tax (GST) and the $1,000 NZD de minimis threshold. 
# Since 2019, New Zealand has required offshore sellers meeting a specific revenue threshold to collect GST at the point of sale 
# for low-value items.
    
# New Zealand Tax & Duty Logic
# The rules for shipping artwork from Mainland China to New Zealand are as follows:
    
# GST (15%): Applied to almost all goods and services, including digital products.
#     Low-Value Goods (≤ $1,000 NZD): If your total sales to NZ consumers exceed $60,000 NZD annually, you must register for and collect 15% GST at checkout.
#     High-Value Goods (> $1,000 NZD): GST is typically collected at the border by New Zealand Customs unless you are registered and choose to collect it upfront.

# Customs Duty: Generally exempt for original works of art.
#     For other physical goods, duty (usually 5–10%) only applies if the total value exceeds the $1,000 NZD de minimis.

# Import Levies: Effective 1 April 2026, a new Low-Value Goods Levy of $2.21 NZD + GST applies to each consignment 
# valued at $1,000 NZD or less to cover border processing.

# Strategic AdviceRegistration Check: 
# If your annual sales to New Zealand are under $60,000 NZD, you do not need to collect GST on low-value orders; 

# New Zealand Customs will simply clear them tax-free at the border.

# Consignments: If a customer places multiple orders that arrive on the same day, Customs may treat them as a single shipment, 
# potentially pushing the total over the $1,000 threshold.print


def calculate_singapore_tax(taxable_value_cny, shipping_cost_cny, exchange_rate, is_ovr_registered=True):
    """
    taxable_value_cny: Value of physical products in CNY
    shipping_cost_cny: Shipping cost in CNY
    exchange_rate: CNY to SGD rate
    is_ovr_registered: Whether your shop is OVR registered (>$100k sales to SG)
    """
    # CIF Value = Cost + Insurance (0 if none) + Freight
    cif_value_cny = taxable_value_cny + shipping_cost_cny
    value_sgd = cif_value_cny * Decimal(exchange_rate)
    
    gst_rate = Decimal('0.09') # 9% for 2024
    gst_amount_cny = Decimal('0.00')
    is_collected_at_checkout = False

    # 1. Low Value Goods (<= S$400)
    if value_sgd <= 400:
        if is_ovr_registered:
            gst_amount_cny = cif_value_cny * gst_rate
            is_collected_at_checkout = True
        else:
            # Not registered? Goods enter GST-free at the border
            gst_amount_cny = Decimal('0.00')
    
    # 2. High Value Goods (> S$400)
    else:
        # GST is paid at the border by the recipient to the courier
        gst_amount_cny = cif_value_cny * gst_rate
        is_collected_at_checkout = False

    return {
        "gst_amount": gst_amount_cny,
        "is_collected_at_checkout": is_collected_at_checkout,
        "note": "Paid at Border" if not is_collected_at_checkout and value_sgd > 400 else ""
    }

# For Singapore, the logic revolves around the Goods and Services Tax (GST) and the S$400 de minimis threshold. Since January 2023, 
# Singapore has implemented the Overseas Vendor Registration (OVR) regime, which significantly changed how GST is collected for low-value imports.
    
# Singapore Tax & Duty Logic
# When shipping artwork from Mainland China to Singapore, the following rules apply:

# GST (9% as of 2024):
#     Low-Value Goods (≤ S$400): If your annual global turnover exceeds S$1 million and your sales to Singapore consumers exceed S$100,000, 
#     you must register for OVR and collect 9% GST at checkout.
#     High-Value Goods (> S$400): GST is always collected at the border by Singapore Customs (usually via the courier), regardless of whether you are OVR-registered.

# Customs Duty: Singapore is a largely free port. Original artwork (paintings, drawings, sculpture) is generally duty-free, though it remains subject to GST.

# Calculation Base: GST is calculated on the CIF value (Cost of goods + Insurance + Freight/Shipping).

# Strategic Advice
# The S$400 Threshold: This is calculated per consignment (the total value of the package), not per item.
# Transparency (Step B in your plan): If the value is > S$400, your frontend should trigger a note explaining that 
# "GST will be collected by the courier upon delivery" so the customer isn't surprised by an extra bill.

# OVR Status: If you are not OVR-registered, your tax calculation for orders under S$400 will simply be 0.00.


def calculate_malaysia_tax(taxable_value_cny, shipping_cost_cny, exchange_rate, is_lvg_registered=True):
    """
    taxable_value_cny: Value of physical products in CNY (excluding shipping)
    shipping_cost_cny: Shipping cost in CNY
    exchange_rate: CNY to MYR rate
    is_lvg_registered: Whether your shop is registered for Malaysia LVG tax
    """
    # 1. Check LVG Threshold (RM 500 based on item price only)
    item_value_myr = taxable_value_cny * Decimal(exchange_rate)
    
    gst_rate_lvg = Decimal('0.10') # 10% for LVG
    sales_tax_high_value = Decimal('0.10') # Standard 10% Sales Tax
    
    tax_amount_cny = Decimal('0.00')
    duty_amount_cny = Decimal('0.00')
    is_collected_at_checkout = False

    # Scenario A: Low Value Goods (<= RM 500)
    if item_value_myr <= 500:
        if is_lvg_registered:
            # Tax is 10% of the ITEM value only (excludes shipping)
            tax_amount_cny = taxable_value_cny * gst_rate_lvg
            is_collected_at_checkout = True
        else:
            # If not registered, customer may be charged at border
            tax_amount_cny = Decimal('0.00')
            
    # Scenario B: High Value Goods (> RM 500)
    else:
        # Duty is typically 0% for original artwork, but Sales Tax applies.
        # Taxes for high-value items are on CIF (Item + Shipping)
        cif_value_cny = taxable_value_cny + shipping_cost_cny
        tax_amount_cny = cif_value_cny * sales_tax_high_value
        is_collected_at_checkout = False

    return {
        "tax_amount": tax_amount_cny,
        "is_collected_at_checkout": is_collected_at_checkout,
        "note": "Payable at checkout" if is_collected_at_checkout else "Payable upon delivery"
    }

# For Malaysia, the tax logic is primarily governed by the Sales and Service Tax (SST) and a specific RM 500 de minimis threshold. 
# Since January 2024, Malaysia has implemented a new tax regime for Low-Value Goods (LVG) imported from overseas.
    
# Malaysia Tax & Duty Logic
# When shipping artwork from Mainland China to Malaysia, these rules apply:
# Sales Tax on Low-Value Goods (LVG): A flat 10% Sales Tax applies to all goods valued at RM 500 or less (excluding shipping and insurance) that are imported into Malaysia.
#     Registration: If your annual sales of LVG to Malaysia exceed RM 500,000, you are required to register and collect this 10% tax at checkout.

# De Minimis Threshold (RM 500):
#     Value ≤ RM 500: Shipments via air courier are exempt from import duty and "Sales Tax on Imports" if the LVG tax (10%) has already been collected at the point of sale.
#     Value > RM 500: These are subject to standard Import Duty (typically 0%–10% for artwork) and Sales Tax on Imports (usually 5% or 10% depending on the item category).

# Calculation Base: Unlike LVG tax (which is on the item price only), standard import duties and taxes for high-value items are calculated on the CIF value (Cost + Insurance + Freight)

# Strategic Advice
#     Item Value vs. Consignment: For the RM 500 threshold, Malaysia looks at the price of the goods only. For high-value imports, they look at the total CIF.
#     Registration: If you don't meet the RM 500,000 annual sales threshold, you aren't mandated to collect the 10% LVG tax; however, couriers may still charge the customer handling fees at the border.


def calculate_korea_tax(taxable_value_cny, shipping_cost_cny, exchange_rate_cny_to_usd):
    """
    taxable_value_cny: Value of physical products in CNY
    shipping_cost_cny: Shipping cost in CNY
    exchange_rate_cny_to_usd: CNY to USD rate (Korea uses USD for threshold check)
    """
    # 1. Check De Minimis in USD (Threshold is $150 for China -> Korea)
    value_usd = taxable_value_cny * Decimal(exchange_rate_cny_to_usd)
    
    vat_rate = Decimal('0.10')
    duty_rate = Decimal('0.08') # Standard duty for many goods; artwork varies
    
    tax_amount_cny = Decimal('0.00')
    duty_amount_cny = Decimal('0.00')
    is_taxable = value_usd > 150

    if is_taxable:
        # Duty is calculated on CIF (Cost + Insurance + Freight)
        cif_value_cny = taxable_value_cny + shipping_cost_cny
        duty_amount_cny = cif_value_cny * duty_rate
        
        # VAT is calculated on (CIF + Duty)
        tax_amount_cny = (cif_value_cny + duty_amount_cny) * vat_rate
    
    return {
        "tax_amount": tax_amount_cny,
        "duty_amount": duty_amount_cny,
        "is_taxable": is_taxable,
        "requires_pccc": True, # Always required for Korea
        "note": "Duties/VAT collected at border" if is_taxable else "Tax Free"
    }

# For South Korea, the calculation is defined by the 10% Value Added Tax (VAT) and a strictly enforced De Minimis threshold 
# of $150 USD (for shipments from Mainland China).

# Korea Tax & Duty LogicKorea is particularly strict about personal imports. Here is the logic for your artwork shop:

# De Minimis Threshold ($150 USD):
#     Value ≤ $150 USD: Exempt from both Customs Duty and VAT.
#     Value > $150 USD: Subject to both Customs Duty (usually 8% for artwork/prints) and VAT (10%).

# VAT (10%): Calculated on the CIF value + Duty.

# Mandatory Requirement (Your Step B/E): Every shipment to Korea requires the recipient's Personal Customs Clearance Code (PCCC) 
# (starts with 'P' followed by 12 digits) or their date of birth if they are a foreigner. 
# Without this, the parcel will be stuck at customs.

# Strategic Advice for your Django Setup
# Step B (Trigger Tip): When destination == 'KR', your frontend must display a notice: "A Personal Customs Clearance Code (PCCC) is required for Korean Customs."
# Step E (Mandatory Field): In your CheckoutInfo and ProformaInvoice, make the destination_tax_id field mandatory if the country is Korea.
# Threshold Note: Note that Korea uses USD for their import threshold check even though the local currency is KRW. Ensure your backend has access to a CNY/USD rate for this specific check.
    

def calculate_japan_tax(taxable_value_cny, shipping_cost_cny, exchange_rate_cny_to_jpy):
    """
    taxable_value_cny: Total value of physical items in CNY
    exchange_rate_cny_to_jpy: Current rate to check ¥10,000 JPY threshold
    """
    # 1. Apply the 60% Personal Import Valuation Rule
    personal_use_valuation_cny = taxable_value_cny * Decimal('0.60')
    valuation_jpy = personal_use_valuation_cny * Decimal(exchange_rate_cny_to_jpy)
    
    consumption_tax_rate = Decimal('0.10')
    tax_amount_cny = Decimal('0.00')
    
    # 2. Check Threshold (Valuation > ¥10,000 JPY)
    # Note: Shipping cost is usually added to the base for tax calculation 
    # if the item value itself exceeds the threshold.
    if valuation_jpy > 10000:
        cif_valuation_cny = personal_use_valuation_cny + shipping_cost_cny
        tax_amount_cny = cif_valuation_cny * consumption_tax_rate

    return {
        "tax_amount": tax_amount_cny,
        "duty_amount": Decimal('0.00'), # Artwork is duty-free
        "is_taxable": valuation_jpy > 10000,
        "note": "Estimated Consumption Tax" if valuation_jpy > 10000 else "Tax Free"
    }


# For Japan, the taxation logic is relatively straightforward but involves a unique 60% valuation rule for personal imports and a 10% Consumption Tax.
    
# Japan Tax & Duty Logic
# When shipping from Mainland China to Japan, the following rules apply:

# De Minimis Threshold (¥10,000 JPY):
#     Total Value ≤ ¥10,000: Generally exempt from both Customs Duty and Consumption Tax.
#     Total Value > ¥10,000: Subject to Consumption Tax and potentially Customs Duty.
# The "Personal Import" Valuation Rule (60%):
#     If the purchase is for personal use (not for resale), Japan Customs often calculates tax based on 60% of the retail price.
#     Example: If an artwork costs ¥20,000, tax is calculated as if it cost ¥12,000.
# Consumption Tax (10%): This is the equivalent of VAT/GST.
# Customs Duty: Original artwork (paintings, engravings, sculptures) is generally Duty-Free in Japan, though the 10% Consumption Tax still applies if over the threshold.

# Strategic Advice
# Step B (Threshold Check): Since Japan's threshold is based on 60% of the price, your "tip info" can reassure customers buying mid-range items ¥
# that they likely won't pay tax unless the 60% value exceeds ¥10,000.

# Courier Fees: Even if duty is 0%, Japanese couriers (like Sagawa or Japan Post) may charge a small "Customs Clearance Fee" (usually ¥200–¥1,000) if tax is collected. 
# You should mention this in your delivery info.


def calculate_taiwan_tax(taxable_value_cny, shipping_cost_cny, exchange_rate_cny_to_twd):
    """
    taxable_value_cny: Total value of physical items in CNY
    shipping_cost_cny: Shipping cost in CNY
    exchange_rate_cny_to_twd: Rate to check NT$2,000 threshold
    """
    # CIF Value in TWD
    cif_value_cny = taxable_value_cny + shipping_cost_cny
    value_twd = cif_value_cny * Decimal(exchange_rate_cny_to_twd)
    
    vat_rate = Decimal('0.05')
    duty_rate = Decimal('0.05') # Typical for prints/artwork
    
    tax_amount_cny = Decimal('0.00')
    duty_amount_cny = Decimal('0.00')
    
    # 1. Check Threshold (NT$2,000)
    if value_twd > 2000:
        # Duty is calculated on CIF
        duty_amount_cny = cif_value_cny * duty_rate
        # VAT is calculated on (CIF + Duty)
        tax_amount_cny = (cif_value_cny + duty_amount_cny) * vat_rate

    return {
        "tax_amount": tax_amount_cny,
        "duty_amount": duty_amount_cny,
        "is_taxable": value_twd > 2000,
        "requires_ezway_id": True,
        "note": "ID and EZ WAY app registration required for customs clearance."
    }

# For Taiwan, the logic is heavily focused on real-name authentication and a relatively low threshold of NT$2,000. 
# This is likely the most "interactive" destination for your frontend.
    
# Taiwan Tax & Duty Logic
# De Minimis Threshold (NT$2,000):
#     Value ≤ NT$2,000: Tax-free (unless the user has exceeded the "6 shipments per half-year" limit).
#     Value > NT$2,000: Subject to Import Duty (typically 5% for artwork) and 5% VAT.

# Frequency Limit: Even if the value is under NT$2,000, if a customer imports more than 6 times in a half-year period (Jan–Jun / Jul–Dec), the 7th shipment is taxable regardless of value.
# Mandatory Requirement (EZ WAY): Recipients must have the EZ WAY (易利委) app installed and registered with their National ID number (or Resident Certificate number for foreigners). Without this, the shipment will be rejected at the border.

# Strategic Advice for your Django-Vite Setup
# Step B (Frontend Tip): When destination == 'TW', trigger a popup or info box: "Taiwan Customs requires real-name authentication via the EZ WAY app. Please ensure your name and phone number match your app registration."
# Step E (Form Validation):
#     Field 1: Recipient Name (must be in Chinese characters if the user is a local citizen).
#     Field 2: National ID Number (10 characters, e.g., A123456789).
#     Field 3: Mobile Phone (must match the one registered in EZ WAY).
# The "6-Times" Rule: Since you cannot know how many times the user has imported from other shops, it is best to add a small disclaimer: "Tax-free status for orders under NT$2,000 only applies if you have not exceeded 6 imports in the current half-year."

def calculate_hong_kong_tax(taxable_value_cny):
    """
    Hong Kong is a free port. No duty or VAT applies to artwork.
    """
    return {
        "tax_amount": Decimal('0.00'),
        "duty_amount": Decimal('0.00'),
        "is_taxable": False,
        "note": "Free Port - No Duty or VAT applied."
    }

# Hong Kong is essentially a free port, meaning that for your artwork shop, 
# there are generally no import duties, VAT, or GST applied to goods entering the territory.

# Hong Kong Tax & Duty Logic
# The rules for shipping artwork from Mainland China to Hong Kong are the simplest among your 9 destinations:
#     Customs Duty (0%): Hong Kong does not impose any general customs tariffs on imported goods.
#     VAT / GST (0%): There is no Value Added Tax or Goods and Services Tax in Hong Kong.
#     Dutiable Commodities: Duties are only levied on four specific types of goods: liquor, tobacco, hydrocarbon oil, and methyl alcohol. As long as your products are strictly artwork or e-products, they are exempt.
#     Import Declaration: While no tax is paid, an import declaration must be lodged within 14 days of the goods' arrival for statistical purposes. This is typically handled by the courier (e.g., SF Express, FedEx) for a small administrative fee.

# Strategic Advice for your Django Setup
#     Step B (Frontend Tip): For Hong Kong, you can display a positive tip: "Enjoy tax-free delivery! Hong Kong is a free port with no import duties or VAT on artwork."
#     Address Selection: Unlike Korea or Taiwan, there are no mandatory ID requirements (like PCCC or EZ WAY) for standard artwork shipments to Hong Kong.
#     Macao: Macao follows a very similar "free port" logic with no general import duties or VAT, making your implementation for Macao identical to Hong Kong

# you can apply the same logic for Macao. Like Hong Kong, Macao is a Free Port and a separate customs territory that does not impose VAT, GST, or general import duties on artwork. [1, 2]
    
# Macao Tax & Duty Logic
# VAT/GST (0%): Macao has no sales tax or Value Added Tax. [2]
# Customs Duty (0%): Artwork is not considered a "dutiable" commodity (which are restricted to things like tobacco, alcohol, and vehicles). [1]
# Import/Export License: For standard artwork, no special license is required for personal or retail imports. [1]
    
# Implementation Advice
# You can simply alias the function in your calculate_tax_duty_api or create a combined "Free Port" check:

def calculate_free_port_tax(taxable_value_cny):
    """Logic for Hong Kong (HK) and Macao (MO)"""
    return {
        "tax_amount": Decimal('0.00'),
        "duty_amount": Decimal('0.00'),
        "is_taxable": False,
        "note": "Free Port - No Duty or VAT applied."
    }
