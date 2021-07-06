from odoo import fields, api, models, _
from odoo.exceptions import AccessError, ValidationError

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    @api.model
    def _get_attachment_file_size(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        return int(get_param('cristo.attachment_file_size', default=25))
    
    def _check_size(self, attachment_ids):
        for attachment_id in attachment_ids:
            if attachment_id and attachment_id.file_size > self._get_attachment_file_size() * 1024 * 1024:
                raise ValidationError(_("The maximum upload File size is %s MB.\n" "File Name: %s") % (self._get_attachment_file_size(), attachment_id.name))