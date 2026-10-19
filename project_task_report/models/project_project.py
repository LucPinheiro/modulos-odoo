# © 2023 i2T Consultoria i Solucions Tecnologiques(<http://www.i2tsite.com>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, models

class ProjectProject(models.Model):
    _inherit = "project.project"

    analyzable_project = fields.Boolean(default=False, string='Analyzable')
