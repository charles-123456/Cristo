from ast import literal_eval
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_token_expiry = fields.Boolean(string="Token Expiry", default=False)
    api_token_time_out_delay = fields.Float(string="Time out delay", default=120)
    api_access_history = fields.Boolean(string='Traceability', default=False)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        api_token_expiry = ICPSudo.get_param('hgp_base.api_token_expiry', False)
        api_token_time_out_delay = ICPSudo.get_param('hgp_base.api_token_time_out_delay', False)
        api_access_history = ICPSudo.get_param('hgp_base.api_access_history', False)
        res.update(
            api_token_expiry=api_token_expiry,
            api_token_time_out_delay=float(api_token_time_out_delay),
            api_access_history=api_access_history,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('hgp_base.api_token_expiry', self.api_token_expiry)
        ICPSudo.set_param('hgp_base.api_token_time_out_delay', float(self.api_token_time_out_delay))
        ICPSudo.set_param('hgp_base.api_access_history', float(self.api_access_history))


