# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import base64
from odoo.tools import ustr
from datetime import datetime

class WizardMeetingEmail(models.TransientModel):
    _name = 'wizard.meeting'
    _description = 'Meeting Mail'
    
    @api.model
    def default_get(self, fields):
        res = super(WizardMeetingEmail, self).default_get(fields)
        user = self.env.user
        mail_server_id = self.env['ir.mail_server'].sudo().search([('partner_id', '=', user.partner_id.id)], limit=1)
        res['mail_server_id'] = mail_server_id.id
        return res
    
    calendar_event_id = fields.Many2one('calendar.event', string="Calendar Event")
    subject = fields.Char(string="Subject")
    body = fields.Html(string="Body")
    attachment_ids = fields.Many2many('ir.attachment', string="Attach Files")
    mail_server_id = fields.Many2one('ir.mail_server', string="Mail Gateway")
    
    def action_meeting_send_email(self):
        email_to =[]
        category = []
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
                raise UserError(_("Connection Test Failed! Check Your Email Connection and Try Again"))
                # raise UserError(_("Connection Test Failed! Here is what we got instead:\n %s") % ustr(e))
            finally:
                try:
                    if smtp:
                        smtp.quit()
                except Exception:
                    pass
                
            # if self.calendar_event_id.attendee_type == 'individual':
            #     for attendee in self.calendar_event_id.partner_ids:
            #         if attendee.email:
            #             email_to.append(attendee.email)
            # elif self.calendar_event_id.attendee_type == 'group':
            #     for attendee in self.calendar_event_id.meeting_group_ids.partner_ids:
            #         if attendee.email:
            #             email_to.append(attendee.email)
            # if self.calendar_event_id.email_to:
            #     email_to.append(self.calendar_event_id.email_to)
            # email_to = ",".join(email_to)

            # if self.calendar_event_id.categ_ids:
            #     for cate_id in self.calendar_event_id.categ_ids:
            #         category.append(cate_id.name)
            #     category = ", ".join(category)

            # if not email_to:
            #     raise UserError(_("Please add Attendees email for the responsible person"))

            # if self.calendar_event_id.start_date and self.calendar_event_id.allday == True:
            #     start_date = datetime.strptime(str(self.calendar_event_id.start_date), "%Y-%m-%d")
            #     start_date = datetime.strftime(start_date, "%d-%m-%Y")
            #     stop_date = datetime.strptime(str(self.calendar_event_id.stop_date), "%Y-%m-%d")
            #     stop_date = datetime.strftime(stop_date, "%d-%m-%Y")
            #
            # elif self.calendar_event_id.start_datetime and self.calendar_event_id.allday == False:
            #     start_date = self.calendar_event_id.convert_utc(str(self.calendar_event_id.start_datetime))
            #     start_date = str(start_date.strftime("%d-%m-%Y %I:%M %p"))
            #     stop_date = False

            template_id = self.env.ref('cristo_calendar_meeting.email_template_meeting_mail_notification', raise_if_not_found=False)
            for attachment in self.attachment_ids:
                bin_data = base64.b64decode(attachment.datas)
                if (len(bin_data) / 1024 / 1024) > 10:
                    raise Warning(_("File size cannot exceed 10MB"))
            if self.attachment_ids:
                template_id.write({'attachment_ids': [(6,0, self.attachment_ids.ids)]})

            for attendee in self.calendar_event_id.attendee_ids:
                if self.calendar_event_id.user_id.partner_id == attendee.partner_id:
                    ex_attendee = attendee
                if template_id:
                    try:
                        template_id.mail_server_id = server.id
                        template_id.with_context(email_from=self.calendar_event_id.user_id.partner_id.email, email_to=attendee.email, subject=self.subject, body_html=self.body, dbname=self._cr.dbname,email_cc=self.calendar_event_id.email_cc).send_mail(attendee.id,force_send=False, raise_exception=True)
                    except MailDeliveryException:
                        raise MailDeliveryException(_("Mail Delivery Failed"), '')

            if self.calendar_event_id.email_to:
                for ex_email in self.calendar_event_id.email_to.split(','):
                    if template_id:
                        try:
                            template_id.mail_server_id = server.id
                            template_id.with_context(email_from=self.calendar_event_id.user_id.partner_id.email, email_to=ex_email, subject=self.subject, body_html=self.body, dbname=self._cr.dbname,email_cc=self.calendar_event_id.email_cc).send_mail(ex_attendee.id, force_send=False,raise_exception=True)
                        except MailDeliveryException:
                            raise MailDeliveryException(_("Mail Delivery Failed"), '')