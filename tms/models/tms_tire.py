from odoo import fields, models


class TmsTireChange(models.Model):
    _name = "tms.tire.change"
    _description = "Truck Tire Change"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc"

    vehicle_id = fields.Many2one("fleet.vehicle", required=True, tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)

    tire_position = fields.Selection(
        [
            ("fl", "Delantera Izq"),
            ("fr", "Delantera Der"),
            ("rl", "Trasera Izq"),
            ("rr", "Trasera Der"),
            ("sp", "Repuesto"),
        ],
        required=True,
        tracking=True,
    )

    brand = fields.Char()
    reference = fields.Char(string="Referencia/Modelo")
    km_at_change = fields.Float(string="KM al cambio")
    notes = fields.Text()
