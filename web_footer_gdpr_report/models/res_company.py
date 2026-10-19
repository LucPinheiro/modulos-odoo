# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    add_gdpr_order = fields.Html()
    add_gdpr_invoice = fields.Html()
