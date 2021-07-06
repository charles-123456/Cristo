# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = 'res.users'
    
    directory_id = fields.Many2one('muk_dms.directory',string="Directory")
    
    def create_directory(self,folder,parent_dir,users):
        directory = self.env['muk_dms.directory'].create({'name':folder,
                                              'parent_directory':parent_dir.id,
                                              'is_main_directory':True,
                                              'institute_id':users.institute_id.id or False,
                                              'rel_province_id':users.rel_province_id.id or False,
                                              'community_id':users.community_id.id or False,
                                              'institution_id':users.institution_id.id or False})
        return directory
    
    def get_root_directory(self,search_name):
        parent_dir = self.env['muk_dms.directory'].search([('is_root_directory','=',True),('name','ilike',search_name)],limit=1)
        if not parent_dir:
            raise ValidationError(_("Sorry! There is no root directory defined for this(%s). Please contact Administrator.") %(search_name))
        else:
            return parent_dir
    
    def check_exist_directory(self, field, id, name,parent_dir):
        dir = self.env['muk_dms.directory'].search([(field,'=',id),('name','ilike',name),('parent_directory','=',parent_dir.id)],limit=1)
        return dir
    
    @api.model
    def create(self, vals):
        users = super(Users, self).create(vals)
        if not users.directory_id:
            directory = False
            if users.has_group('cristo.group_role_cristo_religious_institute_admin'):
                folder_name = "%s-%s" % (users.institute_id.id,users.institute_id.name)
                parent_dir = self.get_root_directory('Congregation')
                dir = self.check_exist_directory('institute_id',users.institute_id.id,users.institute_id.name,parent_dir)
                if dir:
                    directory = dir
                else:
                    directory = self.create_directory(folder_name,parent_dir,users)
            elif users.has_group('cristo.group_role_cristo_religious_province'):
                folder_name = "%s-%s" % (users.rel_province_id.id,users.rel_province_id.name)
                parent_dir = self.get_root_directory('Province')
                dir = self.check_exist_directory('rel_province_id',users.rel_province_id.id,users.rel_province_id.name,parent_dir)
                if dir:
                    directory = dir
                else:
                    directory = self.create_directory(folder_name,parent_dir,users)
            elif users.has_group('cristo.group_role_cristo_religious_house'):
                folder_name = "%s-%s" % (users.community_id.id,users.community_id.name)
                parent_dir = self.get_root_directory('House')
                dir = self.check_exist_directory('community_id',users.community_id.id,users.community_id.name,parent_dir)
                if dir:
                    directory = dir
                else:
                    directory = self.create_directory(folder_name,parent_dir,users)
            elif users.has_group('cristo.group_role_cristo_apostolic_institution'):
                folder_name = "%s-%s" % (users.institution_id.id,users.institution_id.name)
                parent_dir = self.get_root_directory('Institution')
                dir = self.check_exist_directory('institution_id',users.institution_id.id,users.institution_id.name,parent_dir)
                if dir:
                    directory = dir
                else:
                    directory = self.create_directory(folder_name,parent_dir,users)
            elif users.has_group('cristo.group_role_cristo_individual'):
                folder_name = "%s-%s" % (users.partner_id.id,users.partner_id.full_name)
                parent_dir = self.get_root_directory('Member')
                dir = self.check_exist_directory('create_uid',users.id,users.partner_id.full_name,parent_dir)
                if dir:
                    directory = dir
                else:
                    directory = self.create_directory(folder_name,parent_dir,users)
            if directory:
                users.write({'directory_id':directory.id})      
        return users