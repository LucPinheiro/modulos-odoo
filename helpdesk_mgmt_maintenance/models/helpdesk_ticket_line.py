# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)


from dateutil.relativedelta import SU, relativedelta
from datetime import datetime, timedelta
from odoo import models, fields, api

 
class HelpdeskTicketLine(models.Model):
    _name = 'helpdesk.ticket.line'
    _description = 'helpdesk_ticket_line'

    name = fields.Char()
    number = fields.Char('helpdesk.ticket')
    ticket_id = fields.Many2one('helpdesk.ticket')
    ticket_ids = fields.Many2many('helpdesk.ticket')
    date_start = fields.Datetime(default=fields.Datetime.now, required=True)
    date_end = fields.Datetime(string="Check Out")
    total_time = fields.Float(compute="_compute_total_time", store=True)
    value_x = fields.Char(string="Date Name")
    value_y = fields.Char(string="Ticket Name")

 
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        for hours in self:
            if hours.date_end and hours.date_start:
                delta = hours.date_end - hours.date_start
                hours.total_time = delta.total_seconds() / 3600.0
            else:
                hours.total_time = False
    
