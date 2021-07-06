# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
import functools
import operator
import json
from odoo.exceptions import ValidationError
from odoo.addons.cristo.models.res_common import Mail_Excluded_Fields

class File(models.Model):
    _name = 'muk_dms.file'
    _rec_name = 'document_name'
    _inherit = ['common.rel.fields','common.ecc.fields','muk_dms.file','mail.thread']
    _custom_filter_exclude_fields = ['name','color','content_binary','content_file','permission_read','permission_create','permission_write',
                                     'permission_unlink','shared_ids','is_hidden'] + Mail_Excluded_Fields
                                     
    @api.model
    def default_get(self, fields):
        data = super(File, self).default_get(fields)
        if not self._context.get('default_directory',False):
            data['directory'] = self.env.user.directory_id.id or False
        return data
    
    shared_ids = fields.Many2many('res.partner',string="Shared with")
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)
    view_cong_low_lev = fields.Boolean(string="View for Cong. Lower Level")
    view_pro_low_lev = fields.Boolean(string="View for Prov. Lower Level")
    view_house_low_lev = fields.Boolean(string="View for House Lower Level")
    document_name = fields.Char(string="Filename", required=True)
    can_lock = fields.Boolean(compute="_compute_lock_provision")
    name = fields.Char(string="Filename", required=False, index=True)

    def _compute_lock_provision(self):
        for rec in self:
            rec.can_lock = False
            if self.env.user.id == rec.create_uid.id or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
                rec.can_lock = True

    def download_file(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': "{}/web/content?id={}&field=content&model=muk_dms.file&filename_field=name&download=true".format(base_url,self.id),
        }

    @api.onchange('name')
    def _default_document_name(self):
        for rec in self:
            if not rec.document_name:
                rec.document_name = rec.name

    @api.constrains('document_name')
    def _check_name(self):
        for record in self:
            files = record.sudo().directory.files.name_get()
            if list(filter(lambda file: file[1] == record.document_name and file[0] != record.id, files)):
                raise ValidationError(_("A file with the same name already exists."))

    def load_lower_level_sharing(self,field,value,path):
        dir_ids = []
        if value:
            for id in reversed(list(map(int, path.split("/")[:-1]))):
                dir_ids.append(id)
            directory_id = self.env['muk_dms.directory'].browse(dir_ids)
            if directory_id:
                directory_id.write({field:True})
            return directory_id
    
    @api.model
    def create(self, vals):
        file = super(File, self).create(vals)
        dir_ids = []
        for id in reversed(list(map(int, file.directory.parent_path.split("/")[:-1]))):
            dir_ids.append(id)
        directory_id = self.env['muk_dms.directory'].browse(dir_ids)
        shared_ids = file.shared_ids.ids
        partners = []
        for share_id in shared_ids:
            partners.append((4,share_id))
        directory_id.write({'shared_ids':partners})
        self.load_lower_level_sharing('view_cong_low_lev',file.view_cong_low_lev,file.directory.parent_path)
        self.load_lower_level_sharing('view_pro_low_lev',file.view_pro_low_lev,file.directory.parent_path)
        self.load_lower_level_sharing('view_house_low_lev',file.view_house_low_lev,file.directory.parent_path)
        return file 
    
    def write(self, vals):
        part_shared = self.shared_ids.ids
        dir_ids = []
        if part_shared:
            for id in reversed(list(map(int, self.directory.parent_path.split("/")[:-1]))):
                dir_ids.append(id)
            directory_id = self.env['muk_dms.directory'].browse(dir_ids)
            partners = []
            for share in part_shared:
                partners.append((4,share))
            directory_id.write({'shared_ids':partners})   
        file = super(File, self).write(vals)
        self.load_lower_level_sharing('view_cong_low_lev',self.view_cong_low_lev,self.directory.parent_path)
        self.load_lower_level_sharing('view_pro_low_lev',self.view_pro_low_lev,self.directory.parent_path)
        self.load_lower_level_sharing('view_house_low_lev',self.view_house_low_lev,self.directory.parent_path)
        return file
    

    @api.depends('name', 'directory', 'directory.parent_path')
    def _compute_path(self):
        self.path_json = False
        self.path_names = False
        records_with_directory = self - self.filtered(lambda rec: not rec.directory)
        if records_with_directory:
             paths = []
             for rec in records_with_directory:
                 if rec.directory.parent_path:
                    paths = [list(map(int,rec.directory.parent_path.split('/')[:-1]))]
             if paths:
                 model = self.env['muk_dms.directory'].with_context(dms_directory_show_path=False)
                 directories = model.browse(set(functools.reduce(operator.concat, paths)))
                 data = dict(directories._filter_access('read').name_get())
                 for record in self:
                     if record.name:
                        path_names = []
                        path_json = []
                        for id in reversed(list(map(int, record.directory.parent_path.split('/')[:-1]))):
                            if id not in data:
                                    break
                            path_names.append(data[id])
                            path_json.append({
                                    'model': model._name,
                                    'name': data[id],
                                    'id': id,
                                })
                        path_names.reverse()
                        path_json.reverse()
                        name = record.name
                        path_names.append(name)
                        path_json.append({
                            'model': record._name,
                            'name': name,
                            'id': isinstance(record.id, int) and record.id or 0,
                        })
                        record.update({
                            'path_names': '/'.join(path_names),
                            'path_json': json.dumps(path_json),
                        })

