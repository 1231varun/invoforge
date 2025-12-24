"""
Dependency Injection Container

Wires together all dependencies following the Dependency Inversion Principle.
Inner layers (core, application) depend on abstractions, outer layers provide implementations.
"""

from dataclasses import dataclass
from typing import Optional

# Use Cases
from app.application.use_cases.generate_invoice import GenerateInvoiceUseCase
from app.application.use_cases.get_dashboard import GetDashboardUseCase
from app.application.use_cases.get_working_days import GetWorkingDaysUseCase
from app.application.use_cases.manage_leaves import ManageLeavesUseCase
from app.application.use_cases.manage_settings import ManageSettingsUseCase
from app.application.use_cases.preview_invoice import PreviewInvoiceUseCase

# Core Services
from app.core.services.invoice_calculator import InvoiceCalculator
from app.core.services.working_days_calculator import WorkingDaysCalculator
from app.infrastructure.documents.docx_generator import DocxGenerator
from app.infrastructure.documents.html_preview_generator import HTMLPreviewGenerator
from app.infrastructure.documents.pdf_converter import CrossPlatformPDFConverter

# Infrastructure
from app.infrastructure.persistence.database import Database
from app.infrastructure.persistence.sqlite_invoice_repository import SQLiteInvoiceRepository
from app.infrastructure.persistence.sqlite_leave_repository import SQLiteLeaveRepository
from app.infrastructure.persistence.sqlite_settings_repository import SQLiteSettingsRepository


@dataclass
class Container:
    """
    Application dependency container.

    Holds all wired dependencies and use cases.
    """

    # Infrastructure
    database: Database
    invoice_repository: SQLiteInvoiceRepository
    leave_repository: SQLiteLeaveRepository
    settings_repository: SQLiteSettingsRepository
    document_generator: DocxGenerator
    pdf_converter: CrossPlatformPDFConverter
    html_preview_generator: HTMLPreviewGenerator

    # Core Services
    invoice_calculator: InvoiceCalculator
    working_days_calculator: WorkingDaysCalculator

    # Use Cases
    generate_invoice_use_case: GenerateInvoiceUseCase
    preview_invoice_use_case: PreviewInvoiceUseCase
    leaves_use_case: ManageLeavesUseCase
    settings_use_case: ManageSettingsUseCase
    dashboard_use_case: GetDashboardUseCase
    working_days_use_case: GetWorkingDaysUseCase


# Singleton container instance
_container: Optional[Container] = None


def create_container() -> Container:
    """
    Create and wire all dependencies.

    This is the composition root where all dependencies are assembled.
    """
    # Infrastructure layer
    database = Database()

    invoice_repository = SQLiteInvoiceRepository(database)
    leave_repository = SQLiteLeaveRepository(database)
    settings_repository = SQLiteSettingsRepository(database)

    document_generator = DocxGenerator()
    pdf_converter = CrossPlatformPDFConverter()
    html_preview_generator = HTMLPreviewGenerator()

    # Core services
    working_days_calculator = WorkingDaysCalculator()
    invoice_calculator = InvoiceCalculator(working_days_calculator=working_days_calculator)

    # Use cases
    generate_invoice_use_case = GenerateInvoiceUseCase(
        invoice_repository=invoice_repository,
        settings_repository=settings_repository,
        document_generator=document_generator,
        pdf_converter=pdf_converter,
        invoice_calculator=invoice_calculator,
    )

    preview_invoice_use_case = PreviewInvoiceUseCase(
        settings_repository=settings_repository, invoice_calculator=invoice_calculator
    )

    leaves_use_case = ManageLeavesUseCase(leave_repository=leave_repository)

    settings_use_case = ManageSettingsUseCase(settings_repository=settings_repository)

    dashboard_use_case = GetDashboardUseCase(
        invoice_repository=invoice_repository,
        leave_repository=leave_repository,
        settings_repository=settings_repository,
        working_days_calculator=working_days_calculator,
    )

    working_days_use_case = GetWorkingDaysUseCase(
        leave_repository=leave_repository, working_days_calculator=working_days_calculator
    )

    return Container(
        database=database,
        invoice_repository=invoice_repository,
        leave_repository=leave_repository,
        settings_repository=settings_repository,
        document_generator=document_generator,
        pdf_converter=pdf_converter,
        html_preview_generator=html_preview_generator,
        invoice_calculator=invoice_calculator,
        working_days_calculator=working_days_calculator,
        generate_invoice_use_case=generate_invoice_use_case,
        preview_invoice_use_case=preview_invoice_use_case,
        leaves_use_case=leaves_use_case,
        settings_use_case=settings_use_case,
        dashboard_use_case=dashboard_use_case,
        working_days_use_case=working_days_use_case,
    )


def get_container() -> Container:
    """Get the singleton container instance"""
    global _container
    if _container is None:
        _container = create_container()
    return _container


def reset_container():
    """Reset the container (useful for testing)"""
    global _container
    _container = None
