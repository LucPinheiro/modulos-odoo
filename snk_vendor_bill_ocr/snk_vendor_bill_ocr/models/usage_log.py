from odoo import fields, models


class VendorBillOcrUsageLog(models.Model):
    _name = "snk.vendor.bill.ocr.usage.log"
    _description = "Consumo OCR de facturas de proveedor"
    _order = "attempted_at desc, id desc"
    _check_company_auto = True

    company_id = fields.Many2one("res.company", required=True, index=True)
    move_id = fields.Many2one(
        "account.move", string="Factura", required=True, ondelete="cascade", index=True
    )
    attempted_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    status = fields.Selection(
        [
            ("attempted", "Intentada"),
            ("accepted", "Aceptada"),
            ("succeeded", "Completada"),
            ("failed", "Fallida"),
        ],
        required=True,
        default="attempted",
        index=True,
    )
    requested_page_cap = fields.Integer(string="Límite de páginas solicitado")
    page_count = fields.Integer(string="Páginas procesadas")
    http_status = fields.Integer(string="Estado HTTP")
    operation_id = fields.Char(string="Identificador de operación")
    error = fields.Char()

