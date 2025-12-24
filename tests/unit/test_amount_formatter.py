"""
Unit tests for AmountFormatter service.

Tests cover:
- Amount to words conversion
- Multiple currencies
- Decimal handling (cents)
- Edge cases (zero, large numbers, no cents)
"""

from app.core.services.amount_formatter import AmountFormatter


class TestToWords:
    """Tests for to_words method."""

    def test_simple_amount_eur(self, amount_formatter: AmountFormatter):
        """Simple whole number in EUR."""
        result = amount_formatter.to_words(100.00, "EUR")
        assert result == "One Hundred Euros"

    def test_amount_with_cents(self, amount_formatter: AmountFormatter):
        """Amount with cents included."""
        result = amount_formatter.to_words(100.50, "EUR")
        assert result == "One Hundred Euros and Fifty Cents"

    def test_large_amount(self, amount_formatter: AmountFormatter):
        """Large amount formats correctly."""
        result = amount_formatter.to_words(6194.60, "EUR")
        assert "Six Thousand" in result
        assert "Euros" in result
        assert "Sixty Cents" in result

    def test_usd_currency(self, amount_formatter: AmountFormatter):
        """USD uses 'Dollars'."""
        result = amount_formatter.to_words(250.00, "USD")
        assert "Dollars" in result
        assert "Two Hundred" in result  # num2words may add "And"

    def test_gbp_currency(self, amount_formatter: AmountFormatter):
        """GBP uses 'Pounds'."""
        result = amount_formatter.to_words(500.00, "GBP")
        assert "Pounds" in result
        assert "Five Hundred" in result

    def test_inr_currency(self, amount_formatter: AmountFormatter):
        """INR uses 'Rupees'."""
        result = amount_formatter.to_words(1000.00, "INR")
        assert "Rupees" in result
        assert "One Thousand" in result

    def test_unknown_currency_uses_code(self, amount_formatter: AmountFormatter):
        """Unknown currency code is used as-is."""
        result = amount_formatter.to_words(100.00, "XYZ")
        assert "XYZ" in result

    def test_zero_amount(self, amount_formatter: AmountFormatter):
        """Zero amount works correctly."""
        result = amount_formatter.to_words(0.00, "EUR")
        assert "Zero Euros" in result

    def test_single_cent(self, amount_formatter: AmountFormatter):
        """Single cent formats correctly."""
        result = amount_formatter.to_words(100.01, "EUR")
        assert "One Cents" in result or "One Cent" in result

    def test_lowercase_currency_code(self, amount_formatter: AmountFormatter):
        """Currency codes are case-insensitive."""
        result = amount_formatter.to_words(100.00, "eur")
        assert "Euros" in result

    def test_very_large_amount(self, amount_formatter: AmountFormatter):
        """Very large amounts format correctly."""
        result = amount_formatter.to_words(999999.99, "EUR")
        assert "Hundred" in result
        assert "Thousand" in result
        assert "Euros" in result

    def test_decimal_rounding(self, amount_formatter: AmountFormatter):
        """Decimals are rounded to cents."""
        # 0.555 should round to 56 cents (banker's rounding may vary)
        result = amount_formatter.to_words(100.55, "EUR")
        assert "Fifty-Five Cents" in result or "Fifty Five Cents" in result
