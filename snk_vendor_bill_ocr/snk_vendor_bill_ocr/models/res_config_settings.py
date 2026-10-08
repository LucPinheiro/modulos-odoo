from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    vendor_bill_ocr_enabled = fields.Boolean(
        related="company_id.vendor_bill_ocr_enabled", readonly=False
    )
    vendor_bill_ocr_provider = fields.Selection(
        related="company_id.vendor_bill_ocr_provider", readonly=False
    )
    vendor_bill_ocr_azure_endpoint = fields.Char(
        related="company_id.vendor_bill_ocr_azure_endpoint", readonly=False
    )
    vendor_bill_ocr_azure_api_version = fields.Char(
        related="company_id.vendor_bill_ocr_azure_api_version", readonly=False
    )
    vendor_bill_ocr_default_account_id = fields.Many2one(
        related="company_id.vendor_bill_ocr_default_account_id",
        readonly=False,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False), "
        "('account_type', 'in', ('expense', 'expense_depreciation', 'expense_direct_cost'))]",
    )
    vendor_bill_ocr_default_product_id = fields.Many2one(
        related="company_id.vendor_bill_ocr_default_product_id",
        readonly=False,
        domain="[('purchase_ok', '=', True), '|', ('company_id', '=', False), "
        "('company_id', '=', company_id)]",
    )
    vendor_bill_ocr_auto_create_vendor = fields.Boolean(
        related="company_id.vendor_bill_ocr_auto_create_vendor", readonly=False
    )
    vendor_bill_ocr_auto_tax = fields.Boolean(
        related="company_id.vendor_bill_ocr_auto_tax", readonly=False
    )
    vendor_bill_ocr_prices_include_tax = fields.Boolean(
        related="company_id.vendor_bill_ocr_prices_include_tax", readonly=False
    )
    vendor_bill_ocr_require_review = fields.Boolean(
        related="company_id.vendor_bill_ocr_require_review", readonly=False
    )
    vendor_bill_ocr_confidence_threshold = fields.Float(
        related="company_id.vendor_bill_ocr_confidence_threshold", readonly=False
    )
    vendor_bill_ocr_tax_rate_tolerance = fields.Float(
        related="company_id.vendor_bill_ocr_tax_rate_tolerance", readonly=False
    )
    vendor_bill_ocr_amount_tolerance = fields.Float(
        related="company_id.vendor_bill_ocr_amount_tolerance", readonly=False
    )
    vendor_bill_ocr_max_file_mb = fields.Integer(
        related="company_id.vendor_bill_ocr_max_file_mb", readonly=False
    )
    vendor_bill_ocr_max_pages = fields.Integer(
        related="company_id.vendor_bill_ocr_max_pages", readonly=False
    )
    vendor_bill_ocr_daily_limit = fields.Integer(
        related="company_id.vendor_bill_ocr_daily_limit", readonly=False
    )
    vendor_bill_ocr_monthly_limit = fields.Integer(
        related="company_id.vendor_bill_ocr_monthly_limit", readonly=False
    )
    vendor_bill_ocr_max_attempts = fields.Integer(
        related="company_id.vendor_bill_ocr_max_attempts", readonly=False
    )
    vendor_bill_ocr_batch_size = fields.Integer(
        related="company_id.vendor_bill_ocr_batch_size", readonly=False
    )
    vendor_bill_ocr_max_age_days = fields.Integer(
        related="company_id.vendor_bill_ocr_max_age_days", readonly=False
    )
    vendor_bill_ocr_future_days = fields.Integer(
        related="company_id.vendor_bill_ocr_future_days", readonly=False
    )
    vendor_bill_ocr_max_amount = fields.Monetary(
        related="company_id.vendor_bill_ocr_max_amount", readonly=False
    )
    vendor_bill_ocr_store_raw_response = fields.Boolean(
        related="company_id.vendor_bill_ocr_store_raw_response", readonly=False
    )

    vendor_bill_ocr_azure_key = fields.Char(string="Nueva clave de Azure")
    vendor_bill_ocr_key_configured = fields.Boolean(
        string="Clave configurada", compute="_compute_vendor_bill_ocr_key_configured"
    )
    vendor_bill_ocr_clear_key = fields.Boolean(string="Eliminar la clave guardada")

    @api.depends("company_id")
    def _compute_vendor_bill_ocr_key_configured(self):
        params = self.env["ir.config_parameter"].sudo()
        for settings in self:
            settings.vendor_bill_ocr_key_configured = bool(
                params.get_param(
                    "snk_vendor_bill_ocr.azure_key.%s" % settings.company_id.id
                )
            )

    def set_values(self):
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        for settings in self:
            parameter = "snk_vendor_bill_ocr.azure_key.%s" % settings.company_id.id
            if settings.vendor_bill_ocr_clear_key:
                params.set_param(parameter, "")
            elif settings.vendor_bill_ocr_azure_key:
                params.set_param(parameter, settings.vendor_bill_ocr_azure_key.strip())

    def action_vendor_bill_ocr_validate_configuration(self):
        self.ensure_one()
        self.set_values()
        company = self.company_id
        if not company.vendor_bill_ocr_enabled:
            raise UserError(_("Active primero el OCR de facturas de proveedor."))
        if not company.vendor_bill_ocr_azure_endpoint:
            raise UserError(_("Configure el endpoint de Azure."))
        company._vendor_bill_ocr_validate_azure_url(
            company.vendor_bill_ocr_azure_endpoint
        )
        if not company._vendor_bill_ocr_get_api_key():
            raise UserError(_("Configure la clave de Azure."))
        if not company.vendor_bill_ocr_default_account_id:
            raise UserError(_("Configure una cuenta de gasto predeterminada."))
        journal = self.env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", "purchase")], limit=1
        )
        if not journal:
            raise UserError(_("La compañía no tiene ningún diario de compras."))
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Configuración válida"),
                "message": _(
                    "Se usará Azure Document Intelligence prebuilt-invoice. "
                    "La validación no ha consumido páginas."
                ),
                "type": "success",
                "sticky": False,
            },
        }

