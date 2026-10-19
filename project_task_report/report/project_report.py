# © 2023 i2T Consultoria i Solucions Tecnologiques(<http://www.i2tsite.com>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    analyzable_project = fields.Boolean(related='project_id.analyzable_project')
