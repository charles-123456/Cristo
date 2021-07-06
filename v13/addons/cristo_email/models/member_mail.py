from odoo import models, fields,api, _
from odoo.tools import email_split
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError,Warning
from odoo.tools import ustr

STATE = [
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('exception', 'Delivery Failed'),
        ('cancel', 'Cancelled'),
    ]

class Messagebox(models.TransientModel):
    _name = 'message.box'
    _description = 'Message Box'

    message = fields.Text(string="Mail Message", readonly=True, store=True)
    
class MemberMail(models.Model):
    _name = 'member.mail'
    _rec_name = 'mail_subject'
    _inherit = 'attachment.size'
    _description = "Member Mail"
    
    @api.model
    def default_get(self, fields):
        res = super(MemberMail, self).default_get(fields)
        if self._context.get('wizard',False):
            res['recipient_ids'] = [(6,0,self._context.get('active_ids', False))]
        user = self.env.user
        mail_server_id = self.env['ir.mail_server'].search([('partner_id', '=', user.partner_id.id)], limit=1)
        res['mail_from'] = user.email
        res['mail_server_id'] = mail_server_id.id
        if mail_server_id:
            res['from_mail'] = mail_server_id.smtp_user
        res['partner_id'] = user.partner_id.id    
        return res
    
    from_mail = fields.Char(string="From")
    mail_subject = fields.Char(string="Subject")
    mail_from = fields.Char(string="From", help="Message from (emails)")
    mail_to = fields.Char(string="To", help="To recipients")
    body_html = fields.Html('Rich-text Contents', help="Rich-text/HTML message")
    mail_cc = fields.Char('Cc', help="Carbon copy message recipients",size=300)
    mail_bcc = fields.Char('Bcc', help="Blind Carbon Copy message recipients", size=300)
    recipient_ids = fields.Many2many("res.member", string="To")
    state = fields.Selection(STATE,'Status', readonly=True, copy=False, default='outgoing')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    member_list = fields.Char('Member IDS')
    mail_server_id = fields.Many2one('ir.mail_server', string="Mail Gateway")
    partner_id = fields.Many2one('res.partner')
    send_by = fields.Selection([
                                ('individual','Individual'),
                                ('group','Group')
                                ], string="Send by")
    
    @api.constrains('attachment_ids')
    def _check_attachment_size(self):
        self.env['ir.attachment']._check_size(self.attachment_ids)
    
    def mark_cancelled(self):
        return self.write({'state': 'cancel'})
    
    def mark_outgoing(self):
        return self.write({'state': 'outgoing'})
    
    @api.onchange('mail_server_id')
    def _onchange_mail_server(self):
        if self.mail_server_id:
            self.from_mail = self.mail_server_id.smtp_user
            
    @api.depends('recipient_ids')
    @api.onchange('recipient_ids')
    def onchange_recipient_ids(self):
        self.member_list = str(str(self.recipient_ids.ids).strip('[') if self.recipient_ids else '').strip(']')
        
    def send(self, auto_commit=False, raise_exception=False):
        email_list = []
        mail_sent = False
        
#         mail_server_id = self.env['ir.mail_server'].search([('partner_id', '=', self.env.user.partner_id.id)], limit=1).id
        if not self.mail_server_id:
            raise Warning("Sorry! Please configure the Mail Gateway for the User.")
        
        if self.mail_server_id:
            smtp = False
            server = self.env['ir.mail_server'].sudo().search([('id','=',self.mail_server_id.id)])
            try:
                smtp = self.env['ir.mail_server'].connect(server.smtp_host, server.smtp_port, user=server.smtp_user,
                                    password=server.smtp_pass, encryption=server.smtp_encryption,
                                    smtp_debug=server.smtp_debug)
            except Exception as e:
                raise UserError(_("Connection Test Failed! Here is what we got instead:\n %s") % ustr(e))
            finally:
                try:
                    if smtp:
                        smtp.quit()
                except Exception:
                    pass
                
            for mail in self:
                if mail.mail_to:
                    to_email = email_split(mail.mail_to)
                    for to in to_email:
                        email_list.append(to)
                if mail.member_list:
                    member_ids = mail.member_list.split(',')
                    for member in self.env['res.member'].search([('id', 'in', member_ids)]):
                        if member.email:
                            email_list.append(member.email)
                            
                vals = []
                mail_list = []
                if mail.send_by == 'individual':
                    for email in email_list:
                        vals = {
                            'email_from':mail.from_mail,
                            "email_to":email,
                            "subject":mail.mail_subject,
                            "body_html":mail.body_html,
                            "email_cc":mail.mail_cc,
                            "email_bcc":mail.mail_bcc,
                            "reply_to":mail.mail_from,
                            "attachment_ids":[attach.id for attach in mail.attachment_ids],
                            "message_id":False,
                            "references":False,
                            "headers":False,
                            "mail_server_id":mail.mail_server_id.id
                        }
                        
                        mail_id = self.env['mail.mail'].create(vals)
                        mail.write({'state':'sent'})
                elif mail.send_by == 'group':
                    vals = {
                            'email_from':mail.from_mail,
                            "email_to":",".join(email_list),
                            "subject":mail.mail_subject,
                            "body_html":mail.body_html,
                            "email_cc":mail.mail_cc,
                            "email_bcc":mail.mail_bcc,
                            "reply_to":mail.mail_from,
                            "attachment_ids":[attach.id for attach in mail.attachment_ids],
                            "message_id":False,
                            "references":False,
                            "headers":False,
                            "mail_server_id":mail.mail_server_id.id
                        }
                    mail_id = self.env['mail.mail'].create(vals)
                    mail.write({'state':'sent'})
            cron = self.env.ref('mail.ir_cron_mail_scheduler_action')
            return cron.sudo().method_direct_trigger()
                        
#                     mail_list.append(mail_id.id)
#                 mail_list.sort()
#                 for m in mail_list:
#                     try:
#                         mail_id = self.env['mail.mail'].search([('id','=',m)])
#                         res = mail_id.send()
#                         mail.write({'state': 'sent'})
#                         mail_sent = True    
#                     except MailDeliveryException:
#                         raise MailDeliveryException(_("Mail Delivery Failed"), '')
#                 if mail_sent:
#                     return {
#                     'name': 'Cristo Alert',
#                     'type': 'ir.actions.act_window',
#                     'res_model': 'message.box',
#                     'view_mode': 'form',
#                     'target': 'new',
#                     'context':{'default_message':'Mail has been sent successfully.'}
#                     }
#                 else:
#                     return {
#                     'name': 'Cristo Alert',
#                     'type': 'ir.actions.act_window',
#                     'res_model': 'message.box',
#                     'view_mode': 'form',
#                     'target': 'new',
#                     'context':{'default_message':'Mail Delivery Failed.'}
#                     }