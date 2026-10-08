# © 2023 Lu Pinheiro (<https://github.com/Lucpinheiro>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api 
from odoo.exceptions import ValidationError, UserError


class ConnectionType(models.Model):
    _name = "connection.type"
    _description = "Connection Type"

    name = fields.Char()
    attribute_ids = fields.Many2many("attribute")
