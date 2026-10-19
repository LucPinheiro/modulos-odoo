from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tms_route_id = fields.Many2one("tms.route", string="Ruta TMS")
    tms_request_id = fields.Many2one("tms.request", string="Solicitud TMS", readonly=True)

    def action_create_tms_request(self):
        for so in self:
            if so.tms_request_id:
                continue
            if not so.partner_id or not so.tms_route_id:
                continue

            req = self.env["tms.request"].create({
                "partner_id": so.partner_id.id,
                "route_id": so.tms_route_id.id,
                "price": so.amount_total,
                "sale_order_id": so.id,
            })
            so.tms_request_id = req.id
        return True
