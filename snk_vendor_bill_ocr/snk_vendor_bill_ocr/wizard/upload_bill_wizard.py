import base64
import hashlib
import io
import os
import re

from odoo import _, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.mimetypes import guess_mimetype


try:  # Odoo 16 requirements vary with the Python version.
    from PyPDF2 import PdfReader
except ImportError:  # pragma: no cover - depends on the host Python version
    try:
        from PyPDF2 import PdfFileReader as PdfReader
    except ImportError:  # pragma: no cover
        try:
            from pypdf import PdfReader
        except ImportError:  # pragma: no cover
            PdfReader = None


ALLOWED_MIMETYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
}


class VendorBillOcrUploadWizard(models.TransientModel):
    _name = "snk.vendor.bill.ocr.upload.wizard"
    _description = "Digitalizar factura de proveedor"

    bill_file = fields.Binary(
        string="PDF o fotografía de la factura", required=True, attachment=False
    )
    bill_filename = fields.Char(string="Nombre del archivo")
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Diario de compras",
        required=True,
        domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        check_company=True,
        default=lambda self: self.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", self.env.company.id)],
            limit=1,
        ),
    )
    def action_create_bill(self):
        self.ensure_one()
        is_invoice_user = self.env.user.has_group("account.group_account_invoice")
        is_ocr_user = self.env.user.has_group("snk_vendor_bill_ocr.group_vendor_bill_ocr_user")
        if not (is_invoice_user or is_ocr_user):
            raise AccessError(_("No tiene permiso para crear facturas de proveedor."))
        company = self.company_id
        if company not in self.env.user.company_ids:
            raise AccessError(_("No tiene acceso a la compañía seleccionada."))
        if not company.vendor_bill_ocr_enabled:
            raise UserError(
                _("El OCR de facturas de proveedor no está habilitado para la compañía.")
            )
        if (
            not company.vendor_bill_ocr_azure_endpoint
            or not company._vendor_bill_ocr_get_api_key()
        ):
            raise UserError(_("Falta configurar el endpoint o la clave de Azure."))
        company._vendor_bill_ocr_validate_azure_url(
            company.vendor_bill_ocr_azure_endpoint
        )
        if self.journal_id.company_id != company or self.journal_id.type != "purchase":
            raise ValidationError(_("Seleccione un diario de compras de esta compañía."))

        try:
            content = base64.b64decode(self.bill_file, validate=True)
        except (ValueError, TypeError) as error:
            raise ValidationError(_("El archivo adjunto no es válido.")) from error
        if not content:
            raise ValidationError(_("El archivo está vacío."))
        if len(content) > company.vendor_bill_ocr_max_file_mb * 1024 * 1024:
            raise ValidationError(
                _("El archivo supera el máximo configurado de %s MB.")
                % company.vendor_bill_ocr_max_file_mb
            )
        mimetype = self._detect_mimetype(content)
        if mimetype not in ALLOWED_MIMETYPES:
            raise ValidationError(
                _("Formato no admitido (%s). Use PDF, JPEG, PNG o TIFF.") % mimetype
            )

        page_count = self._get_pdf_page_count(content) if mimetype == "application/pdf" else 1
        if page_count and page_count > company.vendor_bill_ocr_max_pages:
            raise ValidationError(
                _(
                    "El PDF tiene %s páginas y el límite configurado es %s. "
                    "Aumente el límite o divida el documento."
                )
                % (page_count, company.vendor_bill_ocr_max_pages)
            )

        digest = hashlib.sha256(content).hexdigest()
        duplicate = self.env["account.move"].sudo().search(
            [
                ("company_id", "=", company.id),
                ("vendor_bill_ocr_document_hash", "=", digest),
            ],
            limit=1,
        )
        if duplicate:
            raise UserError(
                _("Este mismo archivo ya se utilizó en la factura %s.")
                % duplicate.display_name
            )

        filename = self._sanitize_filename(self.bill_filename, mimetype)
        Move = self.env["account.move"].with_company(company).with_context(
            default_move_type="in_invoice"
        )
        bill = Move.create(
            {
                "move_type": "in_invoice",
                "company_id": company.id,
                "journal_id": self.journal_id.id,
                "currency_id": company.currency_id.id,
                "ref": os.path.splitext(filename)[0][:255],
                "to_check": True,
            }
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": self.bill_file,
                "mimetype": mimetype,
                "res_model": "account.move",
                "res_id": bill.id,
            }
        )
        attachment.register_as_main_attachment()
        bill.sudo().write(
            {
                "vendor_bill_ocr_state": "pending",
                "vendor_bill_ocr_provider": "azure",
                "vendor_bill_ocr_document_hash": digest,
                "vendor_bill_ocr_source_attachment_id": attachment.id,
                "vendor_bill_ocr_source_pages": page_count or 0,
                "vendor_bill_ocr_next_retry": fields.Datetime.now(),
            }
        )
        bill.message_post(
            body=_("Factura recibida y pendiente de procesamiento OCR: %s") % filename
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Factura creada desde documento"),
            "res_model": "account.move",
            "res_id": bill.id,
            "view_mode": "form",
            "target": "current",
            "context": {"default_move_type": "in_invoice"},
        }

    @staticmethod
    def _detect_mimetype(content):
        mimetype = guess_mimetype(content, default="application/octet-stream")
        if content.startswith((b"II*\x00", b"MM\x00*")):
            return "image/tiff"
        return mimetype

    @staticmethod
    def _get_pdf_page_count(content):
        if not PdfReader:
            return 0
        try:
            reader = PdfReader(io.BytesIO(content))
            encrypted = bool(
                getattr(reader, "is_encrypted", getattr(reader, "isEncrypted", False))
            )
            if encrypted:
                raise ValidationError(
                    _("El PDF está protegido con contraseña. Guarde una copia sin cifrar.")
                )
            pages = getattr(reader, "pages", None)
            return len(pages) if pages is not None else reader.getNumPages()
        except ValidationError:
            raise
        except Exception as error:
            raise ValidationError(
                _("No se ha podido leer la estructura del PDF; puede estar dañado.")
            ) from error

    @staticmethod
    def _sanitize_filename(filename, mimetype):
        filename = os.path.basename(filename or "").strip()
        filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)
        if filename:
            return filename[:255]
        extension = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/tiff": ".tiff",
        }[mimetype]
        return "factura-proveedor%s" % extension

