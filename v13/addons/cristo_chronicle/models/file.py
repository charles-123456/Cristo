from odoo import models,fields,api

class File(models.Model):
    _inherit = 'muk_dms.file'
    _rec_name = 'document_name'
    
    @api.model
    def default_get(self, fields):
        data = super(File, self).default_get(fields)
        user = self.env.user
        data['directory'] = user.directory_id.id or False
        return data

    is_chronicle = fields.Boolean(string="Is Historical")
    
      
