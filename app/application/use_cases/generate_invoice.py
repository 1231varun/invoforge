"""Generate Invoice Use Case"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from app.core.entities.invoice import Invoice, InvoiceInput
from app.core.interfaces.document_generator import DocumentGenerator
from app.core.interfaces.invoice_repository import InvoiceRepository
from app.core.interfaces.pdf_converter import PDFConverter
from app.core.interfaces.settings_repository import SettingsRepository
from app.core.services.invoice_calculator import InvoiceCalculator


@dataclass
class GenerateInvoiceRequest:
    """Input data for generating an invoice"""

    invoice_number: int
    invoice_date: date
    validity_year: str
    total_working_days: int
    leaves_taken: int
    leave_dates: List[date]
    rate: Optional[float] = None
    output_format: str = "pdf"  # "pdf", "docx", or "both"


@dataclass
class GenerateInvoiceResponse:
    """Result of invoice generation"""

    success: bool
    invoice: Optional[Invoice] = None
    docx_filename: Optional[str] = None
    pdf_filename: Optional[str] = None
    pdf_error: Optional[str] = None
    error: Optional[str] = None


class GenerateInvoiceUseCase:
    """
    Use case for generating invoices.

    Orchestrates:
    1. Getting settings
    2. Calculating invoice values
    3. Generating documents
    4. Converting to PDF
    5. Saving to repository
    """

    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        settings_repository: SettingsRepository,
        document_generator: DocumentGenerator,
        pdf_converter: PDFConverter,
        invoice_calculator: InvoiceCalculator = None,
    ):
        self._invoices = invoice_repository
        self._settings = settings_repository
        self._doc_generator = document_generator
        self._pdf_converter = pdf_converter
        self._calculator = invoice_calculator or InvoiceCalculator()

    def execute(self, request: GenerateInvoiceRequest) -> GenerateInvoiceResponse:
        """Execute the use case"""
        try:
            # Get current settings
            settings = self._settings.get_all()

            # Determine rate
            rate = request.rate if request.rate is not None else settings.daily_rate

            # Create invoice input
            input_data = InvoiceInput(
                invoice_number=request.invoice_number,
                invoice_date=request.invoice_date,
                validity_year=request.validity_year,
                total_working_days=request.total_working_days,
                leaves_taken=request.leaves_taken,
                leave_dates=request.leave_dates,
                rate=rate,
            )

            # Calculate invoice
            invoice = self._calculator.create_invoice(input_data, settings.currency)

            # Determine what to generate
            output_format = request.output_format.lower()
            generate_docx = output_format in ("docx", "both")
            generate_pdf = output_format in ("pdf", "both")

            docx_path = None
            pdf_path = None
            pdf_error = None
            pdf_path_str = None
            docx_path_str = None

            # DOCX is always generated first (PDF needs it as source)
            if generate_docx or generate_pdf:
                docx_path = self._doc_generator.generate(invoice, settings)
                docx_path_str = str(docx_path.absolute())

            # Convert to PDF if requested
            if generate_pdf and docx_path:
                try:
                    pdf_path = self._pdf_converter.convert(docx_path)
                    if pdf_path and pdf_path.exists():
                        pdf_path_str = str(pdf_path.absolute())
                    else:
                        pdf_error = "PDF file was not created"
                except Exception as e:
                    pdf_error = str(e)

                # If only PDF was requested, delete the DOCX
                if output_format == "pdf" and pdf_path and pdf_path.exists():
                    try:
                        docx_path.unlink()  # Delete the DOCX
                        docx_path_str = None
                        docx_path = None
                    except:
                        pass  # Keep DOCX if deletion fails

            # Save to repository
            self._invoices.save(
                invoice_number=invoice.invoice_number,
                invoice_date=invoice.invoice_date,
                service_period_start=invoice.service_period_start,
                service_period_end=invoice.service_period_end,
                days_worked=invoice.days_worked,
                amount=invoice.amount,
                docx_path=docx_path_str or "",
                pdf_path=pdf_path_str,
            )

            return GenerateInvoiceResponse(
                success=True,
                invoice=invoice,
                docx_filename=docx_path.name if docx_path else None,
                pdf_filename=pdf_path.name if pdf_path else None,
                pdf_error=pdf_error,
            )

        except Exception as e:
            return GenerateInvoiceResponse(success=False, error=str(e))
