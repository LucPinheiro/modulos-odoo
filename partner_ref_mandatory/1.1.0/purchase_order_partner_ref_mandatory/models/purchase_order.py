# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_ref = fields.Char()
