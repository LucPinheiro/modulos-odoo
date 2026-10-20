# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    html_translation_state = fields.Selection(
        [("pending", "Pendiente"), ("partial", "En proceso"), ("translated", "Traducido")],
        string="Estado traducción HTML", default="pending", copy=False, index=True,
    )
    html_translation_import_date = fields.Datetime(
        string="Fecha importación HTML", copy=False, readonly=True, index=True,
    )
    html_translation_user_id = fields.Many2one(
        "res.users", string="Importado por", copy=False, readonly=True,
    )
    html_pending_preparation = fields.Boolean(
        string="Pendiente de preparar HTML", default=False, copy=False, index=True,
    )
    standard_import_date = fields.Datetime(
        string="Fecha importación estándar", copy=False, readonly=True,
    )
    html_translation_import_priority = fields.Integer(
        string="Prioridad importación HTML",
        compute="_compute_html_translation_import_priority", store=True, index=True,
    )

    @api.depends("html_translation_state", "html_translation_import_date")
    def _compute_html_translation_import_priority(self):
        for product in self:
            product.html_translation_import_priority = int(bool(
                product.html_translation_import_date
                and product.html_translation_state in ("partial", "translated")
            ))

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("import_file"):
            now = fields.Datetime.now()
            for vals in vals_list:
                vals.update(html_pending_preparation=True,
                            standard_import_date=now, html_translation_state="pending")
        return super().create(vals_list)

    def write(self, vals):
        if self.env.context.get("import_file"):
            vals = dict(vals, html_pending_preparation=True,
                        standard_import_date=fields.Datetime.now())
        return super().write(vals)
