from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TmsMileageSheet(models.Model):
    _name = "tms.mileage.sheet"
    _description = "Driver Mileage Sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc"

    trip_id = fields.Many2one("tms.trip", required=True, ondelete="cascade")
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)

    driver_id = fields.Many2one(related="trip_id.driver_id", store=True, readonly=True)
    vehicle_id = fields.Many2one(related="trip_id.vehicle_id", store=True, readonly=True)

    km_start = fields.Float(tracking=True)
    km_end = fields.Float(tracking=True)
    km_total = fields.Float(compute="_compute_km_total", store=True)

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    fuel_cost = fields.Monetary(currency_field="currency_id")
    other_cost = fields.Monetary(currency_field="currency_id")

    @api.depends("km_start", "km_end")
    def _compute_km_total(self):
        for rec in self:
            rec.km_total = (rec.km_end or 0.0) - (rec.km_start or 0.0)

    @api.constrains("km_start", "km_end")
    def _check_km(self):
        for rec in self:
            if rec.km_start < 0 or rec.km_end < 0:
                raise ValidationError("Los KM no pueden ser negativos.")
            if rec.km_end and rec.km_start and rec.km_end < rec.km_start:
                raise ValidationError("KM fin no puede ser menor que KM inicio.")
