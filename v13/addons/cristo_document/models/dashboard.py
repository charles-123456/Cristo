# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = 'res.member'
    
    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()

        #       Navigation
        doc_action_id = self.env.ref("muk_dms.action_dms_file").id
        doc_menu_id = self.env.ref("muk_dms.main_menu_muk_dms").id
        res[0].update({'doc_action_id': doc_action_id, 'doc_menu_id': doc_menu_id})

        if self.user_has_groups('muk_dms.group_dms_user') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            total_files = self.env['muk_dms.file'].search_count([])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_files = self.env['muk_dms.file'].search_count([('user_id','=',self.env.user.id),('institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_files = self.env['muk_dms.file'].search_count([('user_id','=',self.env.user.id),('rel_province_id','=',self.env.user.rel_province_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                total_files = self.env['muk_dms.file'].search_count([('user_id','=',self.env.user.id),('community_id','=',self.env.user.community_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                total_files = self.env['muk_dms.file'].search_count([('user_id','=',self.env.user.id),('institution_id','=',self.env.user.institution_id.id)])
            res[0].update({'document':1,'total_files':total_files})
        return res