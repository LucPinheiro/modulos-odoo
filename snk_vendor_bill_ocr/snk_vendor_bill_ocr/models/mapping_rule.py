import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VendorBillOcrMappingRule(models.Model):
    _name = "snk.vendor.bill.ocr.mapping.rule"
    _description = "Regla de líneas OCR de factura de proveedor"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Proveedor",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
        help="Vacío aplica a cualquier proveedor.",
    )
    match_type = fields.Selection(
        [("contains", "Contiene"), ("exact", "Exacto"), ("regex", "Expresión regular")],
        required=True,
        default="contains",
    )
    pattern = fields.Char(string="Texto a buscar", required=True)
    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        domain="[('purchase_ok', '=', True), '|', ('company_id', '=', False), "
        "('company_id', '=', company_id)]",
        check_company=True,
        ondelete="restrict",
    )
    account_id = fields.Many2one(
        "account.account",
        string="Cuenta de gasto",
        domain="[('company_id', '=', company_id), ('deprecated', '=', False), "
        "('account_type', 'in', ('expense', 'expense_depreciation', 'expense_direct_cost'))]",
        check_company=True,
        ondelete="restrict",
    )
    tax_ids = fields.Many2many(
        "account.tax",
        string="Impuestos",
        domain="[('company_id', '=', company_id), ('type_tax_use', 'in', ('purchase', 'all')), "
        "('active', '=', True)]",
        check_company=True,
    )

    @api.constrains("pattern", "match_type")
    def _check_pattern(self):
        for rule in self:
            if not (rule.pattern or "").strip():
                raise ValidationError(_("El texto de la regla no puede estar vacío."))
            if rule.match_type == "regex":
                try:
                    re.compile(rule.pattern, re.IGNORECASE)
                except re.error as error:
                    raise ValidationError(
                        _("La expresión regular no es válida: %s") % error
                    ) from error

    @api.constrains("product_id", "account_id", "tax_ids")
    def _check_mapping(self):
        for rule in self:
            if not rule.product_id and not rule.account_id and not rule.tax_ids:
                raise ValidationError(
                    _("La regla debe asignar al menos un producto, cuenta o impuesto.")
                )

    def matches(self, description, partner=None):
        self.ensure_one()
        if self.partner_id and (
            not partner or self.partner_id.commercial_partner_id != partner.commercial_partner_id
        ):
            return False
        candidate = (description or "").strip()
        pattern = (self.pattern or "").strip()
        if self.match_type == "exact":
            return candidate.casefold() == pattern.casefold()
        if self.match_type == "regex":
            return bool(re.search(pattern, candidate, re.IGNORECASE))
        return pattern.casefold() in candidate.casefold()


