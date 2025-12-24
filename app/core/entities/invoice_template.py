"""Invoice Template Entity - Defines customizable invoice sections"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FieldType(Enum):
    """Types of form fields"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    TEXTAREA = "textarea"
    SELECT = "select"
    CURRENCY = "currency"
    READONLY = "readonly"


@dataclass
class TemplateField:
    """A single field in the invoice template"""
    id: str
    label: str
    field_type: FieldType
    default_value: Any = ""
    required: bool = False
    placeholder: str = ""
    options: List[str] = field(default_factory=list)  # For SELECT type
    help_text: str = ""
    section: str = "general"
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.field_type.value,
            "default": self.default_value,
            "required": self.required,
            "placeholder": self.placeholder,
            "options": self.options,
            "help_text": self.help_text,
            "section": self.section,
            "order": self.order
        }


@dataclass
class TemplateSection:
    """A section of the invoice (e.g., Header, Client Details, Services)"""
    id: str
    title: str
    fields: List[TemplateField] = field(default_factory=list)
    order: int = 0
    collapsible: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "fields": [f.to_dict() for f in sorted(self.fields, key=lambda x: x.order)],
            "order": self.order,
            "collapsible": self.collapsible
        }


@dataclass
class InvoiceTemplate:
    """
    Defines the structure and fields of an invoice.
    
    This allows customization of what appears in the invoice and
    how the form is presented to the user.
    """
    id: str
    name: str
    description: str
    sections: List[TemplateSection] = field(default_factory=list)
    currency: str = "EUR"

    def get_section(self, section_id: str) -> Optional[TemplateSection]:
        for section in self.sections:
            if section.id == section_id:
                return section
        return None

    def get_field(self, field_id: str) -> Optional[TemplateField]:
        for section in self.sections:
            for f in section.fields:
                if f.id == field_id:
                    return f
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sections": [s.to_dict() for s in sorted(self.sections, key=lambda x: x.order)],
            "currency": self.currency
        }


def create_default_export_invoice_template() -> InvoiceTemplate:
    """Create the default export invoice template"""
    return InvoiceTemplate(
        id="export-invoice-lut",
        name="Export Invoice (Under LUT)",
        description="Standard export services invoice for Indian freelancers",
        currency="EUR",
        sections=[
            TemplateSection(
                id="invoice_details",
                title="Invoice Details",
                order=1,
                fields=[
                    TemplateField(
                        id="invoice_number",
                        label="Invoice Number",
                        field_type=FieldType.NUMBER,
                        required=True,
                        section="invoice_details",
                        order=1
                    ),
                    TemplateField(
                        id="invoice_date",
                        label="Invoice Date",
                        field_type=FieldType.DATE,
                        required=True,
                        section="invoice_details",
                        order=2
                    ),
                    TemplateField(
                        id="validity_year",
                        label="LUT Validity Year",
                        field_type=FieldType.SELECT,
                        options=["2024-25", "2025-26", "2026-27", "2027-28", "2028-29"],
                        default_value="2025-26",
                        section="invoice_details",
                        order=3
                    )
                ]
            ),
            TemplateSection(
                id="working_days",
                title="Working Days",
                order=2,
                fields=[
                    TemplateField(
                        id="total_working_days",
                        label="Total Working Days",
                        field_type=FieldType.NUMBER,
                        required=True,
                        help_text="Auto-calculated from weekdays minus leaves",
                        section="working_days",
                        order=1
                    ),
                    TemplateField(
                        id="leaves_taken",
                        label="Leaves Taken",
                        field_type=FieldType.READONLY,
                        default_value=0,
                        help_text="Fetched from leave calendar",
                        section="working_days",
                        order=2
                    )
                ]
            ),
            TemplateSection(
                id="billing",
                title="Billing",
                order=3,
                fields=[
                    TemplateField(
                        id="rate",
                        label="Daily Rate",
                        field_type=FieldType.CURRENCY,
                        required=True,
                        placeholder="e.g., 100.00",
                        section="billing",
                        order=1
                    )
                ]
            )
        ]
    )

