from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from datetime import datetime, timedelta
import logging

class UserToken(models.Model):
    _name = "res.user.token"
    _rec_name = "access_token"
    
    user_id = fields.Many2one('res.users', string='User', required=True)
    access_token = fields.Text(string='Token', required=True)
    last_request = fields.Datetime(string='Last Request On')
    
    _sql_constraints = [
        ('access_token_key', 'UNIQUE (access_token)',  'Token Already Exists!')
    ]
    
    @api.model
    def _cron_token_expiry(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        api_token_expiry = ICPSudo.get_param('hgp_base.api_token_expiry', False)
        if api_token_expiry:
            api_token_time_out_delay = ICPSudo.get_param('hgp_base.api_token_time_out_delay', False)
            mins = float(api_token_time_out_delay)
            date = datetime.now()-timedelta(minutes=mins)
            access_token_ids = self.search([('last_request','<=',date.strftime("%Y-%m-%d %H:%M:%S"))])
            if access_token_ids:
                access_token_ids.unlink()
                