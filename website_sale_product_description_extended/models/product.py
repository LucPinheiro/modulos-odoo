# © 2020 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models
from odoo.tools.translate import html_translate


class ProductTemplate(models.Model):
    _inherit = "product.template"

    description_product = fields.Html(
        "Description Product",
        sanitize_attributes=False,
        translate=html_translate,
        copy=False,
    )
    public_shipment = fields.Html(
        "Shipping and Returns",
        sanitize_attributes=False,
        translate=html_translate,
        copy=False,
    )
    payment_methods = fields.Html(
        "Payment Methods for e-Commerce",
        sanitize_attributes=False,
        translate=html_translate,
        copy=False,
    )
