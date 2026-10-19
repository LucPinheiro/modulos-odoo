from odoo import api, fields, models
from odoo.exceptions import UserError


class TmsTrip(models.Model):
    _name = "tms.trip"
    _description = "TMS Trip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("assigned", "Asignado"),
            ("in_transit", "En tránsito"),
            ("delivered", "Entregado"),
            ("closed", "Cerrado"),
            ("cancelled", "Cancelado"),
        ],
        default="draft",
        tracking=True,
        index=True,
    )

    request_id = fields.Many2one("tms.request", string="Solicitud", ondelete="set null")
    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    route_id = fields.Many2one("tms.route", string="Ruta", required=True, tracking=True)

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehículo", tracking=True)
    driver_id = fields.Many2one(
        "res.partner",
        string="Conductor",
        tracking=True,
        domain=[("is_company", "=", False)],
    )

    planned_start = fields.Datetime(tracking=True)
    planned_end = fields.Datetime(tracking=True)
    actual_start = fields.Datetime(tracking=True)
    actual_end = fields.Datetime(tracking=True)

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    price = fields.Monetary(string="Tarifa", currency_field="currency_id", tracking=True)
    extra_costs = fields.Monetary(string="Extras", currency_field="currency_id", tracking=True)
    total = fields.Monetary(string="Total", currency_field="currency_id", compute="_compute_total", store=True)

    invoice_id = fields.Many2one("account.move", string="Factura", readonly=True)
    mileage_sheet_ids = fields.One2many("tms.mileage.sheet", "trip_id", string="Kilometraje")

    @api.depends("price", "extra_costs")
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.price or 0.0) + (rec.extra_costs or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = seq.next_by_code("tms.trip") or "TRP/"
        return super().create(vals_list)

    def action_assign(self):
        self.write({"state": "assigned"})

    def action_start(self):
        self.write({"state": "in_transit", "actual_start": fields.Datetime.now()})

    def action_deliver(self):
        self.write({"state": "delivered", "actual_end": fields.Datetime.now()})

    def action_close(self):
        self.write({"state": "closed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_create_invoice(self):
        for rec in self:
            if rec.invoice_id:
                continue
            if not rec.partner_id:
                raise UserError("Falta el cliente.")

            move = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": rec.partner_id.id,
                "invoice_origin": rec.name,
                "invoice_line_ids": [(0, 0, {
                    "name": f"Servicio de transporte - {rec.route_id.name}",
                    "quantity": 1.0,
                    "price_unit": rec.total,
                })],
            })
            rec.invoice_id = move.id
        return True
