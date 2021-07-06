from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

class RestApiAccessHistory(models.Model):
    _name = 'rest.api.access.history'
    
    user_id = fields.Many2one('res.users', string="User", required=True)
    origin = fields.Char(string='Origin', required=True)
    api_path = fields.Char(string='API Path')
    accessed_on = fields.Datetime(string='Accessed On')
    access_token = fields.Text(string='Token')