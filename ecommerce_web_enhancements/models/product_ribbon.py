# © 2024 Sinerkia_iD - Desarrollo y  Inovación (<https://www.sinerkia.com/)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, tools


class ProductRibbon(models.Model):
    _inherit  = "product.ribbon"
    _description = 'Product ribbon'

    html_class = fields.Selection([
        ('o_ribbon_right', 'Leaning Right'),
        ('o_ribbon_left', 'Leaning left'),
        ('o_tag_left', 'Left label'),
        ('o_tag_right', 'Right label')], string='Ribbon class', required=True, default='o_tag_left'
    )
