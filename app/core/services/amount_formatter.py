"""Amount formatting service"""
from num2words import num2words


class AmountFormatter:
    """Formats monetary amounts into words"""

    CURRENCY_NAMES = {
        "EUR": "Euros",
        "USD": "Dollars",
        "GBP": "Pounds",
        "INR": "Rupees",
    }

    def to_words(self, amount: float, currency: str = "EUR") -> str:
        """
        Convert a monetary amount to words.
        
        Example: 6194.60 EUR -> "Six Thousand, One Hundred Ninety-Four Euros and Sixty Cents"
        """
        currency_name = self.CURRENCY_NAMES.get(currency.upper(), currency)

        whole = int(amount)
        cents = round((amount - whole) * 100)

        whole_words = num2words(whole, lang="en").title()

        if cents > 0:
            cents_words = num2words(cents, lang="en").title()
            return f"{whole_words} {currency_name} and {cents_words} Cents"

        return f"{whole_words} {currency_name}"

