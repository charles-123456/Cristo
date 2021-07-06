from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    attachment_file_size = fields.Integer(string="Attachment Size", default=25, help="Defines the maximum upload size in MB. Default (25MB)")
     
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            attachment_file_size = int(params.get_param('cristo.attachment_file_size', default=25)),
        )
        return res 
      
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('cristo.attachment_file_size', self.attachment_file_size)
        return res

   