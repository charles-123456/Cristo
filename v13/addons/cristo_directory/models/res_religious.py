# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class DirectoryFile(models.Model):
    _name = "res.directory.file"
    _description = "Directory File"

    name = fields.Char(string="Name", required=True)
    file_name = fields.Char(string="File Name")
    file = fields.Binary(string="File", required=True)
    status = fields.Selection([('active','Active'),('inactive','Archive')], string="Status", default='active')
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")

    @api.constrains('status')
    def _active_directory_validation(self):
        for rec in self:
            if rec.status:
                file_id = self.env['res.directory.file'].search_count([('status', '=', 'active'),('rel_province_id', '=', rec.rel_province_id.id)])
                if file_id > 1:
                    raise ValidationError(_("Sorry! You can have only one active file."))

    @api.constrains('file', 'file_name')
    def _check_file(self):
        if self.file and not self.file_name.endswith('.pdf'):
            raise ValidationError('You can upload only pdf file.')

    @api.model
    def download_active_file(self,province=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if province:
            file = self.env['res.directory.file'].search([('status','=','active'),('rel_province_id','=',province)],limit=1)
            if file:
                if file.file:
                    url = "{}/web/content?id={}&field=file&model=res.directory.file&filename_field=file_name&download=true".format(base_url, file.id),
                    return url
                else:
                    raise UserError(_("Sorry! File is not available in the active directory. Upload the file."))
            else:
                raise UserError(_("Sorry! No active directory report found in the Province."))
        else:
            raise UserError(_("Sorry! Province is not found. Contact system admin."))

    @api.model
    def download_directory_file(self, file=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if file:
            url = "{}/web/content?id={}&field=file&model=res.directory.file&filename_field=file_name&download=true".format(
                base_url, file),
            return url


class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'

    file_ids = fields.One2many('res.directory.file', 'rel_province_id', string="Files")

    def open_directory_file(self):
        action = self.env.ref('cristo_directory.action_directory_file').read()[0]
        action.update({
            'domain': [('rel_province_id', '=', self.id)],
            'context': {'default_rel_province_id':self.id},
            'target': 'current',
        })
        return action