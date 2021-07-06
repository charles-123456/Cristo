from odoo import fields, api, models, _

class AttachmentSize(models.AbstractModel):
    _name = "attachment.size"
    _description = "Attachment Size" 
    
    attachment_max_size = fields.Integer(string='Attachment Size', compute='_compute_attachment_file_size')
    
    @api.model
    def default_get(self, fields):
        data = super(AttachmentSize, self).default_get(fields)
        get_param = self.env['ir.config_parameter'].sudo().get_param
        data['attachment_max_size'] = int(get_param('cristo.attachment_file_size', default=25))
        return data
        
    def _compute_attachment_file_size(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        self.attachment_max_size = get_param('cristo.attachment_file_size', default=25)
