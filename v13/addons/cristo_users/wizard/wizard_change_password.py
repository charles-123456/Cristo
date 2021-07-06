from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardChangePassword(models.TransientModel):
    _name = 'wizard.change.password'
    _description = 'Change Password'
    
    new_password = fields.Char(string="New Password")
    cristo_user_id = fields.Many2one('cristo.users',string="User")
    
    def action_change_password(self):
        self.cristo_user_id.write({'password':self.new_password})
        self.cristo_user_id.user_id.write({'password':self.new_password})
        message = _("Password updated successfully.")
        self.env['bus.bus'].sendone(
            (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
            {'type': 'simple_notification', 'title': "Password Update", 'message': message, 'sticky': False, 'warning': False})
