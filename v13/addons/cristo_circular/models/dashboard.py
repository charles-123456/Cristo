# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = 'res.member'
    
    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()

        # Navigation
        cir_action_id = self.env.ref("cristo_circular.action_circular").id
        cir_menu_id = self.env.ref("cristo_circular.cristo_circular_main_menu").id
        res[0].update({'cir_action_id': cir_action_id, 'cir_menu_id': cir_menu_id})

        if self.user_has_groups('cristo_circular.group_circular_user') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            total_circular = self.env['cristo.circular'].search_count([])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_cal = self.env['cristo.circular'].search_count([('user_id','=',self.env.user.id),('institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_cal = self.env['cristo.circular'].search_count([('user_id','=',self.env.user.id),('rel_province_id','=',self.env.user.rel_province_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                total_cal = self.env['cristo.circular'].search_count([('user_id','=',self.env.user.id),('community_id','=',self.env.user.community_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                total_cal = self.env['cristo.circular'].search_count([('user_id','=',self.env.user.id),('institution_id','=',self.env.user.institution_id.id)])
            res[0].update({'circular':1,'total_circular':total_circular})
        return res