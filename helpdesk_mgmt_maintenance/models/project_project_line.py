# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
 
class ProjectProjectLine(models.Model):
    _name = 'project.project.line'
    _description = 'project.project.line'

    name = fields.Char()
    note = fields.Text(String='Description')
    project_id = fields.Many2one('project.project')
    project_ids_count = fields.Integer('project.project', String='Nº Project', compute= '_compute_project_ids_count', store=True)
    equipment_ids = fields.Many2many('maintenance.equipment')
 
    # ---------------------------------
    # DEPENDS METHODS
    # ---------------------------------
    
    @api.depends('project_id')
    def _compute_project_ids_count(self):
        for project in self:
            project.project_ids_count = len(project.project_id)


    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------
    @api.constrains('name')
    def check_name(self):
        for rec in self:
            patients = self.env['project.project.line'].search([('name', '=', rec.name), ('id', '!=', rec.id)])
            if patients:
                raise ValidationError(_("Name %s Already Exists" % rec.name))
    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Project Line'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('project.project.line') or _('New')
        res = super(ProjectProjectLine, self).create(vals)
        return res