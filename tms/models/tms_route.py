from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TmsRoute(models.Model):
    _name = "tms.route"
    _description = "TMS Route"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    origin = fields.Char(required=True, tracking=True)
    destination = fields.Char(required=True, tracking=True)

    distance_km = fields.Float(tracking=True)
    duration_hours = fields.Float(tracking=True)

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    toll_cost = fields.Monetary(currency_field="currency_id", tracking=True)
    suggested_price = fields.Monetary(currency_field="currency_id", tracking=True)

    active = fields.Boolean(default=True)

    @api.constrains("distance_km", "duration_hours")
    def _check_non_negative(self):
        for rec in self:
            if rec.distance_km < 0 or rec.duration_hours < 0:
                raise ValidationError("La distancia y la duración no pueden ser negativas.")
