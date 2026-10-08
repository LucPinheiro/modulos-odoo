# © 2023 Lu Pinheiro (<https://github.com/Lucpinheiro>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api 
from odoo.exceptions import ValidationError, UserError


class Attribute(models.Model):
    _name = "attribute"
    _description = "Attribute"

    name = fields.Char()
