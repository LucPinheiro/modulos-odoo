# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import  models, fields, api

# ---------------------------------
# Project Project:
# ---------------------------------
# Class 1
class ProjectProject(models.Model):
    _inherit = "project.project"

    ticket_ids = fields.Many2many('helpdesk.ticket')
    ticket_count = fields.Integer('helpdesk.ticket', compute='_compute_ticket_count')

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
       for  ticket in self:
            ticket.ticket_count = len(ticket.ticket_ids)
    