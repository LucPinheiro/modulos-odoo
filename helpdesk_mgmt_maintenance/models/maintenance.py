# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  models, fields, api
from odoo.exceptions import ValidationError

# ---------------------------------
# Maintenance Equipment:
# ---------------------------------
# Class 1
class MaintenanceEquipment(models.Model):
    _inherit = ["maintenance.equipment", "image.mixin"]
    _name = "maintenance.equipment"

    request_id = fields.Many2one('maintenance.request')
    request_ids = fields.Many2many('maintenance.request')
    request_stage_id = fields.Many2one('maintenance.stage', related='request_id.request_stage_id', String='Request Stage')
    ticket_id = fields.Char(String='Tickets Number')
    ticket_active = fields.Selection(
        selection=[("yes", "Yes"),("not", "Not")],
        String= "Ticket", default="yes", required=True)
    ticket_ids = fields.Many2many('helpdesk.ticket', String='Tickets Number')
    ticket_count = fields.Integer('helpdesk.ticket', compute='_compute_ticket_count', store=True)
    name_ticket = fields.Char(String='Ticket Name')
    description_ticket = fields.Html(String='Description')
    user_id_ticket = fields.Many2one('helpdesk.ticket')
    stage_id_ticket = fields.Many2one('helpdesk.ticket.stage', String='Stage')
    project_id_ticket = fields.Many2one('project.project', String='Projects') #es heredado de helpdesk
    create_date_ticket = fields.Date()
    last_stage_update_ticket = fields.Datetime(default=fields.Datetime.now)
    category_id_ticket = fields.Many2one('helpdesk.ticket.category', String='Ticket category')
    priority_ticket = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        default="1",
    )
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], String="Tracking", default='serial', required=True)
    model = fields.Char('Model Number', copy=False)
    kanban_state = fields.Selection([('normal', 'In Working'), ('blocked', 'Blocked'), ('scrap', 'Scrap')],
                                    string='Kanban State', required=True, default='normal', tracking=True)
    equipment_brand = fields.Many2one('maintenance.equipment.brand', String='Brand')
   
   
    schedule_date = fields.Datetime('Scheduled Date', help="Date the maintenance team plans the maintenance.  It should not differ much from the Request Date. ")
    create_date = fields.Datetime(String='Creation Date', index=True)
    project_line_ids = fields.Many2many('project.project.line', String='Project Lines')
    project_ids = fields.Many2many('project.project', String='Project Lines')

    # equipment_status_id_count = fields.Integer('maintenance.equipment.status', compute='_compute_equipment_status_id_count')
    equipment_status_id = fields.Many2one('maintenance.equipment.status', String='Status')

    status_id = fields.Selection([
        ('new', 'New'),
        ('repared', 'Repared'),
        ('scrap', 'Scrap')])

    # ---------------------------------
    # DEPENDS METHODS: compute function
    # ---------------------------------

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
       for  ticket in self:
            ticket.ticket_count = len(ticket.ticket_ids)

    @api.depends('project_id')
    def _compute_project_ids_count(self):
        for project in self:
            project.project_ids_count = len(project.project_id)

    # @api.depends('ticket_ids')
    def _compute_ticket_active(self):
        for bool_active in self:
            if bool_active.ticket_ids == True:
                bool_active.ticket_active = "yes"
            else: 
                bool_active.ticket_active = "not"
