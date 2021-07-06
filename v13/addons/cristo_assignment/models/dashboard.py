# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = 'res.member'
    
    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()

#       Navigation
        transfer_action_id = self.env.ref("cristo_assignment.action_assignment").id
        request_action_id = self.env.ref("cristo_assignment.action_assignment_request").id
        transfer_menu_id = self.env.ref("cristo_assignment.assignment_main_menu").id
        res[0].update({'transfer_action_id':transfer_action_id,'request_action_id':request_action_id,'transfer_menu_id':transfer_menu_id})

        if self.user_has_groups('cristo_assignment.group_assignment_admin'):
            total_transfer = self.env['member.assignment'].search_count([])
            total_request = self.env['member.assignment.request'].search_count([])
            res[0].update({'assignment':1,'total_transfer':total_transfer,'total_request':total_request})
            return res
        elif self.user_has_groups('cristo_assignment.group_assignment_manager'):
            total_transfer = self.env['member.assignment'].search_count([('user_id','=',self.env.user.id)])
            total_request = self.env['member.assignment.request'].search_count([('member_id', '=', self.env.user.member_id.id)])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_request = self.env['member.assignment.request'].search_count([('member_id.institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_request = self.env['member.assignment.request'].search_count([('member_id.rel_province_id','=',self.env.user.rel_province_id.id)])
            res[0].update({'assignment':1,'total_transfer':total_transfer,'total_request':total_request})
            return res
        elif self.user_has_groups('cristo_assignment.group_assignment_user'):
            total_request = self.env['member.assignment.request'].search_count([('member_id', '=', self.env.user.member_id.id)])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_request = self.env['member.assignment.request'].search_count([('member_id.institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_request = self.env['member.assignment.request'].search_count([('member_id.rel_province_id','=',self.env.user.rel_province_id.id)])
            res[0].update({'request':1,'total_request':total_request})
            return res
        else:
            return res