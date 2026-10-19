# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class MaintenanceEquipmentStatus(models.Model):
    _name = "maintenance.equipment.status"
    _description = "Maintenance Equipment Status"

    name = fields.Char('Status', required=True, translate=True)
    color = fields.Integer('Color Index')
    sequence = fields.Integer('Sequence', default=20)
    partner_id = fields.Char('res.partner', String= 'Suppliers')
    equipment_ids= fields.Many2many('maintenance.equipment')
    scrap = fields.Boolean('Status Scrap', default=True)
    