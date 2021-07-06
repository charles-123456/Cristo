# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = 'res.member'
    
    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()

        #       Navigation
        con_action_id = self.env.ref("cristo_concern.action_concern").id
        con_menu_id = self.env.ref("cristo_concern.cristo_concern_main_menu").id
        res[0].update({'con_action_id': con_action_id, 'con_menu_id': con_menu_id, })

        if self.user_has_groups('cristo_concern.group_concern_user') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            total_concern = self.env['cristo.concern'].search_count([])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_cal = self.env['cristo.concern'].search_count([('user_id','=',self.env.user.id),('institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_cal = self.env['cristo.concern'].search_count([('user_id','=',self.env.user.id),('rel_province_id','=',self.env.user.rel_province_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                total_cal = self.env['cristo.concern'].search_count([('user_id','=',self.env.user.id),('community_id','=',self.env.user.community_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                total_cal = self.env['cristo.concern'].search_count([('user_id','=',self.env.user.id),('institution_id','=',self.env.user.institution_id.id)])
            res[0].update({'concern':1,'total_concern':total_concern})
        return res