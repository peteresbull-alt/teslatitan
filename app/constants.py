CITIZENSHIP_STATUSES = [
    'US Citizen', 
    'Non-US Citizen',
]

MARITAL_CHOICES = [
    "Married",
    "Single",
    "Divorced",
]

PROGRAM_TYPES = [
    "Short-Term",
    "Long-Term",
]

PREFERRED_CURRENCY = [
    "$",
    "£",
    "€",
    "ILS",
]


EMPLOYMENT_STATUS = [
    "Employed",
    "Self-employed",
    "Unemployed",
    "Retired"
]



ACCOUNT_TYPES = (
    'CHECKING',
    'SAVINGS',
    'PLATINUM', 
    'MONEY MARKET',
)

PREFERRED_ID_TYPE = [
    "Driver Licence",
    "National ID",
    "Passport"
]


EMPLOYMENT_TYPE = [
    "Full-time",
    "Part-time",
    "Contract", 
    "Temporary",
]


PAYMENT_TYPES = [
    "WALLET",
    "BTC",
    "ETH", 
    "CASH APP", 
    "PAYPAL",
]

PAYMENT_METHODS = [
    "WIRE TRANSFER",
    "CRYPTO CURRENCIES",
]


INVESTMENT_TYPES = [
    "Basic Plan",
    "Standard Plan",
    "Premium Plan", 
    "Elite Plan",
]



def generate_currency(currency: str, extract_symbol: bool = True):
    try:
        currency_list = currency.split("-")
        if extract_symbol:
            currency_symbol = currency_list[1].strip()
            return currency_symbol
        else:
            currency_name = currency_list[0].strip()
            return currency_name
    except:
        return ""
    