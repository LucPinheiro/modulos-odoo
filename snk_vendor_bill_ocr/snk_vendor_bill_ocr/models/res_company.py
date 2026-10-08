from datetime import datetime, time
from urllib.parse import parse_qs, urlparse

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


AZURE_ALLOWED_HOST_SUFFIXES = (
    ".cognitiveservices.azure.com",
    ".api.cognitive.microsoft.com",
)


class ResCompany(models.Model):
    _inherit = "res.company"

    vendor_bill_ocr_enabled = fields.Boolean(
        string="OCR de facturas de proveedor habilitado"
    )
    vendor_bill_ocr_provider = fields.Selection(
        [("azure", "Azure Document Intelligence")],
        string="Proveedor OCR de facturas",
        default="azure",
        required=True,
    )
    vendor_bill_ocr_azure_endpoint = fields.Char(
        string="Endpoint de Azure",
        help="Ejemplo: https://mi-recurso.cognitiveservices.azure.com",
    )
    vendor_bill_ocr_azure_api_version = fields.Char(
        string="Versión API de Azure", default="2024-11-30", required=True
    )
    vendor_bill_ocr_default_account_id = fields.Many2one(
        "account.account",
        string="Cuenta de gasto predeterminada",
        domain="[('company_id', '=', id), ('deprecated', '=', False), "
        "('account_type', 'in', ('expense', 'expense_depreciation', 'expense_direct_cost'))]",
        check_company=True,
        ondelete="restrict",
    )
    vendor_bill_ocr_default_product_id = fields.Many2one(
        "product.product",
        string="Producto predeterminado",
        domain="[('purchase_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', id)]",
        check_company=True,
        ondelete="restrict",
        help="Opcional. Se usa cuando Azure no identifica productos concretos.",
    )
    vendor_bill_ocr_auto_create_vendor = fields.Boolean(
        string="Crear proveedor si no existe",
        help="Solo crea el proveedor si Azure devuelve un NIF/VAT. Desactivado por seguridad.",
    )
    vendor_bill_ocr_auto_tax = fields.Boolean(
        string="Asignar impuestos automáticamente", default=True
    )
    vendor_bill_ocr_prices_include_tax = fields.Boolean(
        string="Los precios detectados incluyen impuestos",
        help="Actívelo solo si la mayoría de sus facturas muestran precios unitarios con IVA incluido.",
    )
    vendor_bill_ocr_require_review = fields.Boolean(
        string="Exigir revisión humana", default=True
    )
    vendor_bill_ocr_confidence_threshold = fields.Float(
        string="Confianza mínima", default=0.75
    )
    vendor_bill_ocr_tax_rate_tolerance = fields.Float(
        string="Tolerancia del tipo de impuesto", default=0.25
    )
    vendor_bill_ocr_amount_tolerance = fields.Float(
        string="Tolerancia de importes", default=0.05
    )
    vendor_bill_ocr_max_file_mb = fields.Integer(
        string="Tamaño máximo del archivo (MB)", default=4
    )
    vendor_bill_ocr_max_pages = fields.Integer(
        string="Páginas máximas por documento",
        default=2,
        help="El módulo limita también la petición de Azure a estas páginas.",
    )
    vendor_bill_ocr_daily_limit = fields.Integer(
        string="Peticiones máximas al día",
        default=50,
        help="Cero significa sin límite. Cuenta intentos de envío, incluso si Azure falla.",
    )
    vendor_bill_ocr_monthly_limit = fields.Integer(
        string="Peticiones máximas al mes",
        default=500,
        help="Cero significa sin límite. Cuenta intentos de envío, incluso si Azure falla.",
    )
    vendor_bill_ocr_max_attempts = fields.Integer(
        string="Número máximo de intentos", default=10
    )
    vendor_bill_ocr_batch_size = fields.Integer(
        string="Facturas por ejecución", default=20
    )
    vendor_bill_ocr_max_age_days = fields.Integer(
        string="Antigüedad máxima sin aviso (días)", default=1825
    )
    vendor_bill_ocr_future_days = fields.Integer(
        string="Días futuros permitidos", default=1
    )
    vendor_bill_ocr_max_amount = fields.Monetary(
        string="Importe máximo sin aviso",
        currency_field="currency_id",
        default=0.0,
        help="Cero significa sin límite.",
    )
    vendor_bill_ocr_store_raw_response = fields.Boolean(
        string="Guardar respuesta JSON completa",
        help="Puede contener todo el texto de la factura y datos bancarios.",
    )

    @api.constrains(
        "vendor_bill_ocr_confidence_threshold",
        "vendor_bill_ocr_tax_rate_tolerance",
        "vendor_bill_ocr_amount_tolerance",
        "vendor_bill_ocr_max_file_mb",
        "vendor_bill_ocr_max_pages",
        "vendor_bill_ocr_daily_limit",
        "vendor_bill_ocr_monthly_limit",
        "vendor_bill_ocr_max_attempts",
        "vendor_bill_ocr_batch_size",
        "vendor_bill_ocr_max_age_days",
        "vendor_bill_ocr_future_days",
        "vendor_bill_ocr_max_amount",
    )
    def _check_vendor_bill_ocr_values(self):
        for company in self:
            if not 0 <= company.vendor_bill_ocr_confidence_threshold <= 1:
                raise ValidationError(_("La confianza mínima debe estar entre 0 y 1."))
            if company.vendor_bill_ocr_tax_rate_tolerance < 0:
                raise ValidationError(_("La tolerancia fiscal no puede ser negativa."))
            if company.vendor_bill_ocr_amount_tolerance < 0:
                raise ValidationError(_("La tolerancia de importes no puede ser negativa."))
            positive_fields = (
                company.vendor_bill_ocr_max_file_mb,
                company.vendor_bill_ocr_max_pages,
                company.vendor_bill_ocr_max_attempts,
                company.vendor_bill_ocr_batch_size,
            )
            if any(value <= 0 for value in positive_fields):
                raise ValidationError(
                    _("Tamaño, páginas, intentos y lote deben ser mayores que cero.")
                )
            nonnegative_fields = (
                company.vendor_bill_ocr_daily_limit,
                company.vendor_bill_ocr_monthly_limit,
                company.vendor_bill_ocr_max_age_days,
                company.vendor_bill_ocr_future_days,
                company.vendor_bill_ocr_max_amount,
            )
            if any(value < 0 for value in nonnegative_fields):
                raise ValidationError(_("Los límites OCR no pueden ser negativos."))

    @api.constrains("vendor_bill_ocr_azure_endpoint")
    def _check_vendor_bill_ocr_endpoint(self):
        for company in self.filtered("vendor_bill_ocr_azure_endpoint"):
            company._vendor_bill_ocr_validate_azure_url(
                company.vendor_bill_ocr_azure_endpoint
            )

    def _vendor_bill_ocr_validate_azure_url(self, url, operation_url=False):
        self.ensure_one()
        parsed = urlparse((url or "").strip())
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValidationError(_("El endpoint OCR debe ser una URL HTTPS válida."))
        if parsed.username or parsed.password or parsed.fragment:
            raise ValidationError(_("La URL OCR no puede contener credenciales ni fragmento."))
        if not operation_url and (parsed.query or parsed.path not in ("", "/")):
            raise ValidationError(_("El endpoint OCR no puede contener ruta ni consulta."))
        host = parsed.hostname.lower().rstrip(".")
        if not any(host.endswith(suffix) for suffix in AZURE_ALLOWED_HOST_SUFFIXES):
            raise ValidationError(
                _(
                    "El host debe pertenecer a cognitiveservices.azure.com "
                    "o api.cognitive.microsoft.com."
                )
            )
        if operation_url:
            configured_host = urlparse(
                self.vendor_bill_ocr_azure_endpoint or ""
            ).hostname
            if configured_host and host != configured_host.lower().rstrip("."):
                raise ValidationError(
                    _("Azure devolvió una operación desde un host inesperado.")
                )
            allowed_paths = ("/documentintelligence/", "/formrecognizer/")
            if not parsed.path.lower().startswith(allowed_paths):
                raise ValidationError(_("La ruta de seguimiento de Azure no es válida."))
            unexpected = set(parse_qs(parsed.query)) - {"api-version"}
            if unexpected:
                raise ValidationError(
                    _("La URL de operación contiene parámetros inesperados.")
                )
        return parsed

    def _vendor_bill_ocr_get_api_key(self):
        self.ensure_one()
        return self.env["ir.config_parameter"].sudo().get_param(
            "snk_vendor_bill_ocr.azure_key.%s" % self.id, ""
        )

    def _vendor_bill_ocr_check_and_log_quota(self, move):
        """Count before POST: conservative limits also cover lost responses."""
        self.ensure_one()
        now = fields.Datetime.now()
        # Serialize quota checks for a company to avoid concurrent overshoot.
        self.env.cr.execute("SELECT id FROM res_company WHERE id = %s FOR UPDATE", [self.id])
        Log = self.env["snk.vendor.bill.ocr.usage.log"].sudo()
        day_start = datetime.combine(now.date(), time.min)
        month_start = day_start.replace(day=1)
        if self.vendor_bill_ocr_daily_limit:
            used_today = Log.search_count(
                [("company_id", "=", self.id), ("attempted_at", ">=", day_start)]
            )
            if used_today >= self.vendor_bill_ocr_daily_limit:
                raise UserError(
                    _("Se alcanzó el límite diario de %s peticiones OCR.")
                    % self.vendor_bill_ocr_daily_limit
                )
        if self.vendor_bill_ocr_monthly_limit:
            used_month = Log.search_count(
                [("company_id", "=", self.id), ("attempted_at", ">=", month_start)]
            )
            if used_month >= self.vendor_bill_ocr_monthly_limit:
                raise UserError(
                    _("Se alcanzó el límite mensual de %s peticiones OCR.")
                    % self.vendor_bill_ocr_monthly_limit
                )
        return Log.create(
            {
                "company_id": self.id,
                "move_id": move.id,
                "attempted_at": now,
                "status": "attempted",
                "requested_page_cap": self.vendor_bill_ocr_max_pages,
            }
        )
