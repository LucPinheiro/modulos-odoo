# © 2023 Lucia Pinero Consultoría Informática (<http://www.luciapinero.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  models, fields, api


# ---------------------------------
# Tracealibity:
# ---------------------------------
# Class 1
class Tracealibity(models.Model):
    _name = "tracealibity"
    _description = "Tracealibity Equipments"

    name = fields.Char(required=True)
    equipment_id = fields.Many2one('maintenance.equipment', String= 'Equipments', required=True)
    serial_no = fields.Char('maintenance.equipment', related='equipment_id.serial_no', String='Serial Number')
    model_equipament = fields.Char('maintenance.equipment', related='equipment_id.model', String ='Modal')
    equipment_start_date = fields.Date()
    equipment_end_date = fields.Date()

    tracking = fields.Selection([
    ('serial', 'By Unique Serial Number'),
    ('lot', 'By Lots'),
    ('none', 'No Tracking')], String="Tracking", default='serial', required=True)
    