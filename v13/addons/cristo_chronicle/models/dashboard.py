# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from datetime import date,datetime

class Member(models.Model):
    _inherit = 'res.member'
    
    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()

#       Navigation
        mychr_action_id = self.env.ref("cristo_chronicle.action_my_chronicle").id
        chr_action_id = self.env.ref("cristo_chronicle.action_other_chronicle").id
        chr_menu_id = self.env.ref("cristo_chronicle.cristo_chronicler_main_menu").id
        res[0].update({'mychr_action_id': mychr_action_id, 'chr_action_id': chr_action_id,
                       'chr_menu_id': chr_menu_id})

        if self.user_has_groups('cristo_chronicle.group_role_cristo_chronicle_read') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            total_chr = self.env['cristo.chronicle'].search_count([])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_chr = self.env['cristo.chronicle'].search_count([('user_id','=',self.env.user.id),('institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_chr = self.env['cristo.chronicle'].search_count([('user_id','=',self.env.user.id),('rel_province_id','=',self.env.user.rel_province_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                total_chr = self.env['cristo.chronicle'].search_count([('user_id','=',self.env.user.id),('community_id','=',self.env.user.community_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                total_chr = self.env['cristo.chronicle'].search_count([('user_id','=',self.env.user.id),('institution_id','=',self.env.user.institution_id.id)])
            res[0].update({'chronicle':1,'total_chr':total_chr})
        return res