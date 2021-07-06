# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class EmailGateway(models.Model):
    _inherit = "ir.mail_server"
    _description = "Email Server"
    
    @api.model
    def default_get(self, fields):
        res = super(EmailGateway, self).default_get(fields)
        user = self.env.user
        res['smtp_host'] = "smtp.gmail.com"
        res['smtp_encryption'] = 'ssl'
        res['partner_id'] = user.partner_id.id
        return res
    
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.smtp_user:
                result.append((record.id, "{} [{}]".format(record.name, record.smtp_user)))
            else:
                result.append((record.id,record.name))
        return result
    
    name = fields.Char(string='Description', required=True, index=True)    
    partner_id = fields.Many2one('res.partner', string="Partner")
    smtp_user = fields.Char(string='Username', help="Optional username for SMTP authentication", groups='base.group_system,base.group_user')
    smtp_pass = fields.Char(string='Password', help="Optional password for SMTP authentication", groups='base.group_system,base.group_user')
