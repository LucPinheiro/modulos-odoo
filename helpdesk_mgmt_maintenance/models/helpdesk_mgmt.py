# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  _, models, fields, api
from odoo.exceptions import ValidationError

# ---------------------------------
# Helpdesk Ticket: 
# ---------------------------------
# Class 1

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"


    ticket_ids_line = fields.One2many(
         'helpdesk.ticket.line', 'ticket_id',
         String='Ticket Lines')
    equipment_id = fields.Many2one('maintenance.equipment', String= 'Equipments', required=True)
    employee_id_hr = fields.Many2one('hr.employee', String= 'Equipments')
    equipment_ids = fields.Many2many('maintenance.equipment', String= 'Equipments')
    equipment_ids_count = fields.Integer('maintenance.equipment', compute= '_compute_equipment_ids_count', store=True)
    employee_id = fields.Many2one('hr.employee', related='equipment_id.employee_id')
    departament_id = fields.Many2one('hr.department')
    serial_no = fields.Char('maintenance.equipment', related='equipment_id.serial_no', String='Serial Number')
    model_equipament = fields.Char('maintenance.equipment', related='equipment_id.model', String ='Modal')
    category_id = fields.Many2one('maintenance.equipment.category', related='equipment_id.category_id')
    cost = fields.Float('maintenance.equipment', related='equipment_id.cost', String='Cost')
    description_equipment = fields.Html(String='Description')
    date_start = fields.Datetime(default=fields.Datetime.now, required=True)
    date_end = fields.Datetime(string="Check Out")
    total_time = fields.Float(compute="_compute_total_time", store=True)
    value_x = fields.Char(string="Date Name")
    value_y = fields.Char(string="Ticket Name")
    default_date_end = fields.Date('helpdesk.ticket')
    closed_date = fields.Datetime()
    project_id = fields.Many2one('project.project', string='Project')
    project_id_count = fields.Integer('project.project', compute= '_compute_project_id_count', store=True)
    task_id = fields.Many2one('project.task', string='Task')
    task_id_count = fields.Integer('project.task', compute= '_compute_task_id_count', store=True)
    initially_date = fields.Datetime(default=fields.Datetime.now)
    planned_hours = fields.Float(string="Planned hours")
    total_hour = fields.Float(string="Total hours", compute='_compute_total_hour')

    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], String="Tracking", default='serial', required=True)
    
 
    # ---------------------------------
    # DEPENDS METHODS
    # ---------------------------------
    
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        for hours in self:
            if hours.date_end and hours.date_start:
                delta = hours.date_end - hours.date_start
                hours.total_time = delta.total_seconds() / 3600.0
            else:
                hours.total_time = False

    @api.depends('initially_date', 'closed_date')
    def _compute_total_hour(self):
        for hours in self:
            if hours.closed_date and hours.initially_date:
                delta = hours.closed_date - hours.initially_date
                hours.total_hour = delta.total_seconds() / 3600.0
            else:
                hours.total_hour = False

    @api.depends('equipment_ids')
    def _compute_equipment_ids_count(self):
        for equipment in self:
            equipment.equipment_ids_count = len(equipment.equipment_ids)

    @api.depends('project_id')
    def _compute_project_id_count(self):
        for project in self:
            project.project_id_count = len(project.project_id)

    @api.depends('task_id')
    def _compute_task_id_count(self):
        for tack in self:
            tack.task_id_count = len(tack.task_id)

