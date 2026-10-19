# © 2023 Lucia Pinero Consultoría Informática (<http://www.luciapinero.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)


from email.policy import default
from odoo import fields, models, api
import calendar, datetime

class MaintenanceEquipmentWizard(models.TransientModel):
    _name = 'maintenance.equipment.report.wizard'
    _description = 'Maintenance Equipment Report Wizard'

    @api.model
    def _default_first_day_month(self):
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        return datetime.date(year,month,1)
    
    @api.model
    def _default_last_day_month(self):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        last_day = calendar.monthrange(year, month)[1] ## last day

        return datetime.date(year,month,last_day)

    date_start = fields.Date('Start Date', default=_default_first_day_month)
    date_end = fields.Date('End Date', default=_default_last_day_month)
    

    def action_search_orders(self):
        form_data = self.read()[0]

        orders = self.env['maintenance.equipment.line'].search_read([
            ('create_date', '>=', form_data['date_start']),
            ('create_date', '<=', form_data['date_end'])
        ])

        data = {
            'form_data': form_data,
            'orders': orders
        }

        return self.env.ref('helpdesk_mgmt_maintenance.action_report_equipment').report_action(self, data=data)
    