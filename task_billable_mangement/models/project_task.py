# © 2023 i2T Consultoria i Solucions Tecnologiques(<http://www.i2tsite.com>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, api, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_status = fields.Selection(
        selection=[
            ("backlog", "Backlog"),
            ("to_do", "To Do"),
            ("doing", "Doing"),
            ("done", "Done"),
            ("reject", "Reject"),
        ], default="backlog")
    project_id = fields.Many2one('project.project', string='Project')
    
    @api.model_create_multi
    def create(self, vals_list):
        current_user = self.env.user
        is_project_manager = current_user.has_group("project.group_project_manager")
        for vals in vals_list:
            project_id = vals.get('project_id')
            if project_id:
                project_id = self.env['project.project'].browse(project_id)
                if project_id.user_id and project_id.user_id != current_user:
                    if project_id and is_project_manager == False:
                        raise UserError(_(
                            "Tasks cannot be created. Contact your manager."))
        task = super(ProjectTask, self).create(vals_list)
        return task

    @api.constrains('project_id')
    def _check_project_id(self):
            for task in self:
                if not task.project_id:
                    raise ValidationError(_('You cannot create a task without a project.'))

    def write(self, vals):
        current_user = self.env.user
        is_project_manager = current_user.has_group("project.group_project_manager")
        for rec in self:
            if rec.project_id.allow_billable == False:
                continue
            if vals.get('task_status', False) and rec.task_status in ["done", "reject"]:
                if rec.project_id.user_id == current_user:
                    continue
                elif not is_project_manager:
                    raise AccessError(_(
                        "Only administrators can change from done or reject status."))
        return super(ProjectTask, self).write(vals)
