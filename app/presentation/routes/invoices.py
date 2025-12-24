"""Invoice API routes"""

from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from app.application.use_cases.generate_invoice import GenerateInvoiceRequest
from app.application.use_cases.preview_invoice import PreviewInvoiceRequest
from app.container import get_container

invoices_bp = Blueprint("invoices", __name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"


@invoices_bp.route("/generate", methods=["POST"])
def generate():
    """Generate a new invoice"""
    data = request.json
    container = get_container()

    try:
        invoice_date = datetime.strptime(data["invoice_date"], "%Y-%m-%d").date()
        leave_dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in data.get("leave_dates", [])]

        # Parse optional service period
        service_period_start = None
        service_period_end = None
        if data.get("service_period_start"):
            service_period_start = datetime.strptime(
                data["service_period_start"], "%Y-%m-%d"
            ).date()
        if data.get("service_period_end"):
            service_period_end = datetime.strptime(data["service_period_end"], "%Y-%m-%d").date()

        req = GenerateInvoiceRequest(
            invoice_number=int(data["invoice_number"]),
            invoice_date=invoice_date,
            validity_year=data["validity_year"],
            total_working_days=int(data["total_working_days"]),
            leaves_taken=int(data.get("leaves_taken", 0)),
            leave_dates=leave_dates,
            rate=float(data["rate"]) if data.get("rate") else None,
            output_format=data.get("output_format", "pdf"),
            service_period_start=service_period_start,
            service_period_end=service_period_end,
        )

        response = container.generate_invoice_use_case.execute(req)

        if response.success:
            return jsonify(
                {
                    "success": True,
                    "invoice": {
                        "number": response.invoice.invoice_number,
                        "date": response.invoice.invoice_date.isoformat(),
                        "service_period": response.invoice.service_period,
                        "days_worked": response.invoice.days_worked,
                        "amount": response.invoice.amount,
                        "amount_in_words": response.invoice.amount_in_words,
                    },
                    "files": {
                        "docx": response.docx_filename,
                        "pdf": response.pdf_filename,
                        "pdf_error": response.pdf_error,
                    },
                }
            )
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@invoices_bp.route("/preview", methods=["POST"])
def preview():
    """Preview invoice calculations"""
    data = request.json
    container = get_container()

    try:
        invoice_date = datetime.strptime(data["invoice_date"], "%Y-%m-%d").date()
        leave_dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in data.get("leave_dates", [])]

        # Parse optional service period
        service_period_start = None
        service_period_end = None
        if data.get("service_period_start"):
            service_period_start = datetime.strptime(
                data["service_period_start"], "%Y-%m-%d"
            ).date()
        if data.get("service_period_end"):
            service_period_end = datetime.strptime(data["service_period_end"], "%Y-%m-%d").date()

        req = PreviewInvoiceRequest(
            invoice_number=int(data["invoice_number"]),
            invoice_date=invoice_date,
            validity_year=data["validity_year"],
            total_working_days=int(data["total_working_days"]),
            leaves_taken=int(data.get("leaves_taken", 0)),
            leave_dates=leave_dates,
            rate=float(data["rate"]) if data.get("rate") else None,
            service_period_start=service_period_start,
            service_period_end=service_period_end,
        )

        response = container.preview_invoice_use_case.execute(req)

        if response.success:
            return jsonify(
                {
                    "success": True,
                    "preview": {
                        "service_period": response.service_period,
                        "days_worked": response.days_worked,
                        "amount": response.amount,
                        "total_payable": response.total_payable,
                        "amount_in_words": response.amount_in_words,
                    },
                }
            )
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@invoices_bp.route("/preview-html", methods=["POST"])
def preview_html():
    """Generate live HTML preview of the invoice"""
    data = request.json
    container = get_container()

    try:
        settings = container.settings_repository.get_all()

        # Parse the date
        if data.get("invoice_date"):
            data["invoice_date"] = datetime.strptime(data["invoice_date"], "%Y-%m-%d").date()

        # Generate HTML preview
        html = container.html_preview_generator.generate_from_data(data, settings)

        return jsonify({"success": True, "html": html})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@invoices_bp.route("/invoices", methods=["GET"])
def list_invoices():
    """List all invoices"""
    container = get_container()

    try:
        invoices = container.invoice_repository.get_all()
        return jsonify(
            {
                "success": True,
                "invoices": [inv.to_dict() for inv in invoices],
                "count": len(invoices),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@invoices_bp.route("/invoices/<int:invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id: int):
    """Delete an invoice and its associated files"""
    container = get_container()

    try:
        # Get the invoice record first to get file paths
        invoice = container.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            return jsonify({"success": False, "error": "Invoice not found"}), 404

        # Delete associated files
        files_deleted = []
        for file_path in [invoice.docx_path, invoice.pdf_path]:
            if file_path:
                path = Path(file_path)
                if path.exists():
                    try:
                        path.unlink()
                        files_deleted.append(path.name)
                    except Exception as e:
                        print(f"Warning: Could not delete file {file_path}: {e}")

        # Delete from database
        success = container.invoice_repository.delete(invoice_id)

        # Get the new next invoice number
        next_number = container.invoice_repository.get_next_number()

        return jsonify(
            {"success": success, "files_deleted": files_deleted, "next_invoice_number": next_number}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@invoices_bp.route("/next-invoice-number")
def next_invoice_number():
    """Get the next invoice number"""
    container = get_container()

    return jsonify({"success": True, "next_number": container.invoice_repository.get_next_number()})


@invoices_bp.route("/invoices/<int:invoice_id>/preview", methods=["GET"])
def preview_stored_invoice(invoice_id: int):
    """Generate preview HTML for a stored invoice"""
    container = get_container()

    try:
        invoice_record = container.invoice_repository.get_by_id(invoice_id)
        if not invoice_record:
            return jsonify({"success": False, "error": "Invoice not found"}), 404

        settings = container.settings_repository.get_all()

        # Generate preview HTML using the stored invoice data
        html = container.html_preview_generator.generate_from_record(invoice_record, settings)

        return jsonify({"success": True, "html": html})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@invoices_bp.route("/download/<filename>")
def download(filename: str):
    """Download a generated file"""
    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        return jsonify({"error": f"File not found: {filename}"}), 404

    return send_file(str(filepath.absolute()), as_attachment=True, download_name=filename)
