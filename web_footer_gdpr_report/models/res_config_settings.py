# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    add_gdpr_order = fields.Html(
        related='company_id.add_gdpr_order',
        string='GDPR Order',
        readonly=False,
    )
    add_gdpr_invoice = fields.Html(
        related='company_id.add_gdpr_invoice',
        string='GDPR Invoice',
        readonly=False,
    )

