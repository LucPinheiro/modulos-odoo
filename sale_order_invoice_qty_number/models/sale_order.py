# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_ids = fields.Many2many("account.move")
    invoice_number_count = fields.Integer(compute= '_compute_invoice_number_count', string='Invoice count', store= True)

    @api.depends('order_line.invoice_lines')
    def _compute_invoice_number_count(self):
        for invoice in self:
            invoice.invoice_number_count = len(invoice.invoice_ids)
