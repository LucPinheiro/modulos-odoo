# © 2023 Lu Pinheiro (<https://github.com/Lucpinheiro>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models

class City(models.Model):
    _name = "city"
    _description = "City"

    name = fields.Char(string="City")
   