# © 2023 i2T Consultoria i Solucions Tecnologiques(<http://www.i2tsite.com>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"
    
    task_status = fields.Selection('Status', related='task_id.task_status')

    @api.constrains('task_id')
    def _check_timesheet_constraints(self):
        for rec in self:
            if rec.task_id.allow_billable and rec.task_id.task_status != "doing":
                raise UserError(_(
                    'Hours can only be assigned to tasks with a status of "In Process" if they are billable'))
