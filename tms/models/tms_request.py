from odoo import api, fields, models


class TmsRequest(models.Model):
    _name = "tms.request"
    _description = "TMS Transport Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("confirmed", "Confirmada"),
            ("planned", "Planificada"),
            ("cancelled", "Cancelada"),
        ],
        default="draft",
        tracking=True,
        index=True,
    )

    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    route_id = fields.Many2one("tms.route", string="Ruta", required=True, tracking=True)

    pickup_date = fields.Datetime(tracking=True)
    delivery_date = fields.Datetime(tracking=True)

    cargo_description = fields.Text(string="Descripción de carga")
    weight_kg = fields.Float(string="Peso (kg)")
    volume_m3 = fields.Float(string="Volumen (m³)")

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    price = fields.Monetary(string="Tarifa", currency_field="currency_id", tracking=True)
    extra_costs = fields.Monetary(string="Extras", currency_field="currency_id", tracking=True)
    total = fields.Monetary(string="Total", currency_field="currency_id", compute="_compute_total", store=True)

    sale_order_id = fields.Many2one("sale.order", string="Orden de Venta", readonly=True)
    trip_id = fields.Many2one("tms.trip", string="Viaje", readonly=True)

    @api.depends("price", "extra_costs")
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.price or 0.0) + (rec.extra_costs or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = seq.next_by_code("tms.request") or "TRQ/"
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_plan(self):
        self.write({"state": "planned"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_create_trip(self):
        for rec in self:
            if rec.trip_id:
                continue
            trip = self.env["tms.trip"].create({
                "request_id": rec.id,
                "partner_id": rec.partner_id.id,
                "route_id": rec.route_id.id,
                "planned_start": rec.pickup_date,
                "planned_end": rec.delivery_date,
                "price": rec.price,
                "extra_costs": rec.extra_costs,
            })
            rec.trip_id = trip.id
            rec.state = "planned"
        return True
