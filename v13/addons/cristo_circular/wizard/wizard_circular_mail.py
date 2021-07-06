from odoo import api, fields, models, _
from lxml import etree
import json
import base64
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

class WizardCircularMail(models.TransientModel):
    _name = "circular.mail"
    _description = "Circular Mail"
    
    @api.model
    def default_get(self, fields):
        res = super(WizardCircularMail, self).default_get(fields)
        user = self.env.user
        partner_ids = self.env['res.partner']
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
            partner_ids = self.env['res.partner'].search([('main_category_code','in',['RP','HC','RI','MR'])])
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            partner_ids = self.env['res.partner'].search([('main_category_code','in',['HC','RI','MR'])])
        if self.user_has_groups('cristo.group_role_cristo_religious_house'):
            partner_ids = self.env['res.partner'].search([('main_category_code','in',['RI','MR'])])
        if self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            partner_ids = self.env['res.partner'].search([('main_category_code','=','MR')])
        res['rel_province_id'] = user.rel_province_id.id
        if res.get('status',False):
            if res['status'] == 'all':
                res['partner_ids'] = partner_ids.ids
        return res
    
    from_mail = fields.Char(string="From")
    subject = fields.Char(string="Subject")
    email_from = fields.Char(string="From", help="Message from (emails)")
    body = fields.Html('Rich-text Contents', help="Rich-text/HTML message")
    mail_server_id = fields.Many2one('ir.mail_server', string="Mail Gateway")
    partner_ids = fields.Many2many('res.partner', string="To")
    rel_province_id = fields.Many2one("res.religious.province")
    circular_id = fields.Many2one('cristo.circular', string="Circular")
    attachment_id = fields.Many2one('ir.attachment',string="Attachment")
    group_ids = fields.Many2many('meeting.group', string="Group")
    status = fields.Selection([('all','All'),('group','Group'),('individual','Individual')], string="Status")
    
    @api.onchange('mail_server_id')
    def _onchange_mail_server(self):
        if self.mail_server_id:
            self.email_from = self.mail_server_id.smtp_user
    
    @api.onchange('group_ids')
    def _onchange_group(self):
        if self.group_ids:
            for group_id in self.group_ids:
                self.partner_ids = [(6,0,group_id.partner_ids.ids)]
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(WizardCircularMail, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self._context.get('default_status') == 'individual':
            for node in doc.xpath("//field[@name='partner_ids']"):
                node.set("domain", "[('main_category_code','=','MR')]")                     
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    def action_send_mail(self):
        email_to = []
        report_template = self.env.ref('cristo_circular.report_circular').report_action(self)
        template_id = self.env.ref('cristo_circular.email_template_circular_mail', raise_if_not_found=False)
        if self.status == 'all':
            for partner in self.partner_ids:
                if partner.email:
                    email_to.append(partner.email)
        elif self.status == 'group':
            for partner in self.partner_ids:
                if partner.email:
                    email_to.append(partner.email)
        else:
            for partner in self.partner_ids:
                if partner.email:
                    email_to.append(partner.email)

        email_to = ",".join(email_to)
        if self.circular_id.type == 'create_content':
            if template_id:
                try:
                    template_id.mail_server_id = self.mail_server_id.id
                    template_id.write({'report_template': self.env['ir.actions.report'].search([('id', '=', 298)], limit=1).id})
                    template_id.with_context(email_from=self.email_from, email_to=email_to, subject=self.subject, body=self.body).send_mail(self.circular_id.id,force_send=False, raise_exception=True)
                except MailDeliveryException:
                    raise MailDeliveryException(_("Mail Delivery Failed"), '')
        elif self.circular_id.type == 'upload':
            if template_id:
                if self.attachment_id:
                    template_id.write({'attachment_ids': [(6,0, [self.attachment_id.id])]})
                else:
                    template_id.write({'attachment_ids': False})
                try:
                    template_id.mail_server_id = self.mail_server_id.id
                    template_id.with_context(email_from=self.email_from, email_to=email_to, subject=self.subject, body=self.body).sudo().send_mail(self.circular_id.id,force_send=False, raise_exception=True)
                except MailDeliveryException:
                    raise MailDeliveryException(_("Mail Delivery Failed"), '')
