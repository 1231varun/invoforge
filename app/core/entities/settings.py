"""Settings domain entity"""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Settings:
    """Application settings / configuration"""
    # Billing
    daily_rate: float = 0.0
    currency: str = "EUR"

    # Supplier (Your business)
    supplier_name: str = ""
    supplier_address: str = ""
    gstin: str = ""
    pan: str = ""
    supplier_email: str = ""

    # Export
    place_of_supply: str = ""
    lut_no: str = ""
    lut_validity: str = "2025-26"

    # Client
    client_name: str = ""
    client_address: str = ""
    client_country: str = ""
    client_email: str = ""

    # Service
    service_description: str = "Professional / IT / Consulting Services (SAC: 9983)"

    # Bank
    bank_name: str = ""
    account_no: str = ""
    account_holder: str = ""
    swift_code: str = ""

    # Signature
    signatory_name: str = ""  # Name that appears on signature line

    # System
    setup_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "daily_rate": self.daily_rate,
            "currency": self.currency,
            "supplier_name": self.supplier_name,
            "supplier_address": self.supplier_address,
            "gstin": self.gstin,
            "pan": self.pan,
            "supplier_email": self.supplier_email,
            "place_of_supply": self.place_of_supply,
            "lut_no": self.lut_no,
            "lut_validity": self.lut_validity,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "client_country": self.client_country,
            "client_email": self.client_email,
            "service_description": self.service_description,
            "bank_name": self.bank_name,
            "account_no": self.account_no,
            "account_holder": self.account_holder,
            "swift_code": self.swift_code,
            "signatory_name": self.signatory_name,
            "setup_complete": self.setup_complete
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """Create Settings from dictionary, handling type conversions"""
        return cls(
            daily_rate=float(data.get("daily_rate", 0)),
            currency=data.get("currency", "EUR"),
            supplier_name=data.get("supplier_name", ""),
            supplier_address=data.get("supplier_address", ""),
            gstin=data.get("gstin", ""),
            pan=data.get("pan", ""),
            supplier_email=data.get("supplier_email", ""),
            place_of_supply=data.get("place_of_supply", ""),
            lut_no=data.get("lut_no", ""),
            lut_validity=data.get("lut_validity", "2025-26"),
            client_name=data.get("client_name", ""),
            client_address=data.get("client_address", ""),
            client_country=data.get("client_country", ""),
            client_email=data.get("client_email", ""),
            service_description=data.get("service_description", "Professional / IT / Consulting Services (SAC: 9983)"),
            bank_name=data.get("bank_name", ""),
            account_no=data.get("account_no", ""),
            account_holder=data.get("account_holder", ""),
            swift_code=data.get("swift_code", ""),
            signatory_name=data.get("signatory_name", ""),
            setup_complete=str(data.get("setup_complete", "false")).lower() == "true"
        )

