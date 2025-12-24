"""
HTML Preview Generator - Renders invoice as HTML matching DOCX output exactly.

This generates an HTML preview that mirrors the structure and styling
of the generated DOCX document for accurate visual representation.
"""

from calendar import monthrange
from datetime import date
from typing import Any, Dict

from app.core.entities.invoice import Invoice, InvoiceRecord
from app.core.entities.settings import Settings
from app.core.services.amount_formatter import AmountFormatter


class HTMLPreviewGenerator:
    """
    Generates HTML preview of an invoice that matches the DOCX output.
    """

    def generate(self, invoice: Invoice, settings: Settings) -> str:
        """Generate HTML preview matching DOCX structure exactly"""
        return self._render_document(invoice, settings)

    def generate_from_data(self, data: Dict[str, Any], settings: Settings) -> str:
        """Generate preview from form data (before full invoice creation)"""
        # Parse invoice date
        invoice_date = data.get("invoice_date", date.today())
        if isinstance(invoice_date, str):
            invoice_date = date.fromisoformat(invoice_date)

        # Calculate service period
        first_day = date(invoice_date.year, invoice_date.month, 1)
        last_day_num = monthrange(invoice_date.year, invoice_date.month)[1]
        last_day = date(invoice_date.year, invoice_date.month, last_day_num)

        # Calculate values
        rate = float(data.get("rate", settings.daily_rate) or 0)
        working_days = int(data.get("total_working_days", 0) or 0)
        leaves = int(data.get("leaves_taken", 0) or 0)
        days_worked = working_days - leaves
        amount = round(days_worked * rate, 2)

        # Format amount in words
        formatter = AmountFormatter()
        amount_words = formatter.to_words(amount, settings.currency)

        # Parse leave dates
        leave_dates = data.get("leave_dates", [])
        leave_dates_formatted = []
        for d in leave_dates:
            if isinstance(d, str) and d:
                leave_dates_formatted.append(d)
            elif hasattr(d, "isoformat"):
                leave_dates_formatted.append(d.isoformat())

        validity_year = data.get("validity_year", "2025-26")
        invoice_number = data.get("invoice_number", "—")

        # Build HTML matching DOCX structure exactly
        return self._render_html(
            invoice_number=invoice_number,
            invoice_date=invoice_date.isoformat(),
            service_period_start=first_day.isoformat(),
            service_period_end=last_day.isoformat(),
            supplier_name=settings.supplier_name,
            supplier_address=settings.supplier_address,
            gstin=settings.gstin,
            pan=settings.pan,
            supplier_email=settings.supplier_email,
            place_of_supply=settings.place_of_supply,
            lut_no=settings.lut_no,
            validity_year=validity_year,
            client_name=settings.client_name,
            client_address=settings.client_address,
            client_country=settings.client_country,
            client_email=settings.client_email,
            total_working_days=working_days,
            leaves_taken=leaves,
            leave_dates=leave_dates_formatted,
            service_description=settings.service_description,
            days_worked=days_worked,
            rate=rate,
            amount=amount,
            currency=settings.currency,
            amount_in_words=amount_words,
            account_holder=settings.account_holder,
            account_no=settings.account_no,
            bank_name=settings.bank_name,
            swift_code=settings.swift_code,
            signatory_name=settings.signatory_name,
        )

    def generate_from_record(self, record: InvoiceRecord, settings: Settings) -> str:
        """Generate preview from a stored InvoiceRecord"""
        # Calculate rate from stored data
        rate = record.amount / record.days_worked if record.days_worked > 0 else settings.daily_rate

        # Format amount in words
        formatter = AmountFormatter()
        amount_words = formatter.to_words(record.amount, settings.currency)

        # Determine validity year from invoice date
        year = record.invoice_date.year
        month = record.invoice_date.month
        if month >= 4:  # April onwards is next FY
            validity_year = f"{year}-{str(year + 1)[-2:]}"
        else:
            validity_year = f"{year - 1}-{str(year)[-2:]}"

        return self._render_html(
            invoice_number=record.invoice_number,
            invoice_date=record.invoice_date.isoformat(),
            service_period_start=record.service_period_start.isoformat(),
            service_period_end=record.service_period_end.isoformat(),
            supplier_name=settings.supplier_name,
            supplier_address=settings.supplier_address,
            gstin=settings.gstin,
            pan=settings.pan,
            supplier_email=settings.supplier_email,
            place_of_supply=settings.place_of_supply,
            lut_no=settings.lut_no,
            validity_year=validity_year,
            client_name=settings.client_name,
            client_address=settings.client_address,
            client_country=settings.client_country,
            client_email=settings.client_email,
            total_working_days=record.days_worked,  # We only store days_worked
            leaves_taken=0,  # Not stored in record
            leave_dates=[],  # Not stored in record
            service_description=settings.service_description,
            days_worked=record.days_worked,
            rate=rate,
            amount=record.amount,
            currency=settings.currency,
            amount_in_words=amount_words,
            account_holder=settings.account_holder,
            account_no=settings.account_no,
            bank_name=settings.bank_name,
            swift_code=settings.swift_code,
            signatory_name=settings.signatory_name,
        )

    def _render_document(self, invoice: Invoice, settings: Settings) -> str:
        """Render from Invoice object"""
        leave_dates = [
            d.isoformat() if hasattr(d, "isoformat") else str(d) for d in invoice.leave_dates
        ]

        return self._render_html(
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date.isoformat(),
            service_period_start=invoice.service_period_start.isoformat(),
            service_period_end=invoice.service_period_end.isoformat(),
            supplier_name=settings.supplier_name,
            supplier_address=settings.supplier_address,
            gstin=settings.gstin,
            pan=settings.pan,
            supplier_email=settings.supplier_email,
            place_of_supply=settings.place_of_supply,
            lut_no=settings.lut_no,
            validity_year=invoice.validity_year,
            client_name=settings.client_name,
            client_address=settings.client_address,
            client_country=settings.client_country,
            client_email=settings.client_email,
            total_working_days=invoice.total_working_days,
            leaves_taken=invoice.leaves_taken,
            leave_dates=leave_dates,
            service_description=settings.service_description,
            days_worked=invoice.days_worked,
            rate=invoice.rate,
            amount=invoice.amount,
            currency=settings.currency,
            amount_in_words=invoice.amount_in_words,
            account_holder=settings.account_holder,
            account_no=settings.account_no,
            bank_name=settings.bank_name,
            swift_code=settings.swift_code,
            signatory_name=settings.signatory_name,
        )

    def _render_html(self, **kwargs) -> str:
        """Render the HTML matching DOCX structure exactly"""

        # Format supplier address
        address_html = ""
        if kwargs.get("supplier_address"):
            for line in kwargs["supplier_address"].replace("\\n", "\n").split("\n"):
                if line.strip():
                    address_html += f'<p class="line">{line}</p>\n'

        # Format leave dates
        leave_dates_html = ""
        for d in kwargs.get("leave_dates", []):
            leave_dates_html += f'<p class="line">{d}</p>\n'

        # Get signature name - use signatory_name if set, otherwise fall back to supplier_name
        signature_name = kwargs.get("signatory_name", "")
        if not signature_name and kwargs.get("supplier_name"):
            # Extract name without parenthetical as fallback
            signature_name = kwargs["supplier_name"].split("(")[0].strip()

        return f"""
<div class="invoice-header">EXPORT INVOICE (UNDER LUT)</div>

<div class="section">
    <p class="line">Invoice No.: {kwargs.get("invoice_number", "—")}</p>
    <p class="line">Invoice Date: {kwargs.get("invoice_date", "—")}</p>
    <p class="line section-end">Service Period: {kwargs.get("service_period_start", "—")} to {kwargs.get("service_period_end", "—")}</p>
</div>

<div class="section">
    <p class="line">{kwargs.get("supplier_name", "")}</p>
    {address_html}
    <p class="line tight">GSTIN: {kwargs.get("gstin", "—")}</p>
    <p class="line tight">PAN: {kwargs.get("pan", "—")}</p>
    <p class="line section-end">Email: {kwargs.get("supplier_email", "—")}</p>
</div>

<div class="section">
    <p class="line">Place of Supply: {kwargs.get("place_of_supply", "—")}</p>
    <p class="line">Type: Export of Services without Payment of IGST (Under LUT)</p>
    <p class="line section-end">LUT No.: {kwargs.get("lut_no", "—")}     Validity: FY {kwargs.get("validity_year", "—")}</p>
</div>

<div class="section">
    <p class="line"><strong>Bill To:</strong></p>
    <p class="line">Name:  {kwargs.get("client_name", "—")}</p>
    <p class="line">Address:  {kwargs.get("client_address", "—")}</p>
    <p class="line section-end">Country: {kwargs.get("client_country", "—")}    Email: {kwargs.get("client_email", "—")}</p>
</div>

<div class="section">
    <p class="line"><strong>Total No. of working days:</strong> {kwargs.get("total_working_days", 0)}</p>
    <p class="line"><strong>Leaves Taken:</strong> {kwargs.get("leaves_taken", 0)}</p>
    {leave_dates_html}
    <p class="line section-end"></p>
</div>

<table class="services-table">
    <tr>
        <td class="header-cell"><strong>Description of Services:</strong></td>
    </tr>
    <tr>
        <td class="content-cell">1. {kwargs.get("service_description", "Professional Services")} | Days: {kwargs.get("days_worked", 0)} | Rate: {kwargs.get("currency", "EUR")} {kwargs.get("rate", 0):.2f} | Amount: {kwargs.get("currency", "EUR")} {kwargs.get("amount", 0):.2f}</td>
    </tr>
</table>

<div class="section">
    <p class="line">Tax: Export Without Payment of IGST under LUT</p>
    <p class="line">Total Payable ({kwargs.get("currency", "EUR")}): {kwargs.get("amount", 0):.2f}</p>
    <p class="line section-end">Total in Words: {kwargs.get("amount_in_words", "—")}</p>
</div>

<div class="section">
    <p class="line section-end">Bank Details: {kwargs.get("account_holder", "—")} | A/c No: {kwargs.get("account_no", "—")} | Bank: {kwargs.get("bank_name", "—")} | SWIFT: {kwargs.get("swift_code", "—")}</p>
</div>

<div class="section">
    <p class="line section-end">Declaration: This invoice is issued as Export of Services without payment of IGST under LUT as per Sec. 16 of IGST Act. Payment will be received in foreign currency. No GST charged.</p>
</div>

<div class="section signature">
    <p class="line">For {kwargs.get("account_holder", "—")}</p>
    <p class="line">{signature_name}</p>
</div>
"""
