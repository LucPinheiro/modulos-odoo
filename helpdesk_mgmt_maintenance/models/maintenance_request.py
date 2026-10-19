# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, SUPERUSER_ID, _


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    
    request_stage_id = fields.Many2one('maintenance.stage', string='Stage')
    equipment_ids = fields.Many2many('maintenance.equipment')
    equipment_ids_count = fields.Integer('maintenance.equipment', compute= '_compute_equipment_ids_count', store=True, String= 'Nº Equipment')
    equipment_brand = fields.Many2one('maintenance.equipment.brand', related='equipment_ids.equipment_brand',String='Brand')
    equipment_status_id = fields.Many2one('maintenance.equipment.status', related='equipment_ids.equipment_status_id', String='Status')
    status_id = fields.Selection('maintenance.equipment', related='equipment_ids.status_id')  
    new_status_id_count = fields.Integer('maintenance.equipment',
            compute='_compute_status_count', String='Nº Status')
    repared_status_id_count = fields.Integer('maintenance.equipment',
            compute='_compute_status_count', String='Nº Status')
    scrap_status_id_count = fields.Integer('maintenance.equipment',
            compute='_compute_status_count', String='Nº Status')
    ticket_ids = fields.Many2many('helpdesk.ticket', related='equipment_ids.ticket_ids', String='Tickets Number')
    ticket_count = fields.Integer('helpdesk.ticket', compute='_compute_ticket_count', store=True, String= 'Nº Ticket')
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], String="Tracking", default='serial', required=True)


    # ---------------------------------
    # DEPENDS METHODS: compute function
    # ---------------------------------

    @api.depends('equipment_ids')
    def _compute_equipment_ids_count(self):
        for equipment in self:
            equipment.equipment_ids_count = len(equipment.equipment_ids)

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
       for  ticket in self:
            ticket.ticket_count = len(ticket.ticket_ids)

    @api.depends('equipment_ids')
    def _compute_status_count(self):
            for status in self:
                status.new_status_id_count = len(status.equipment_ids.filtered(lambda x: x.status_id == "new")) 
                status.repared_status_id_count = len(status.equipment_ids.filtered(lambda x: x.status_id == "repared"))
                status.scrap_status_id_count = len(status.equipment_ids.filtered(lambda x: x.status_id == "scrap"))

    # ---------------------------------
    # Actions METHODS: Email function
    # ---------------------------------
    def _find_mail_template(self, force_confirmation_template=False):
        self.ensure_one()
        template_id = False

        if force_confirmation_template or (self.stage_id == 'Repaired' and not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('request.default_confirmation_template'))
            template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data']._xmlid_to_res_id('request.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data']._xmlid_to_res_id('request.email_template_edi_request', raise_if_not_found=False)

        return template_id
    
    def _send_order_confirmation_mail(self):
        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)
        for order in self:
            template_id = order._find_mail_template(force_confirmation_template=True)
            if template_id:
                order.with_context(force_send=True).message_post_with_template(template_id, composition_mode='comment', email_layout_xmlid="mail.mail_notification_paynow")
    

    def action_send_email(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'maintenance.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
