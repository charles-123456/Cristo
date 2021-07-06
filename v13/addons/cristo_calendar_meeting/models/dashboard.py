# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from datetime import date,datetime

class Member(models.Model):
    _inherit = 'res.member'
    
    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()

        #Navigation
        cal_action_id = self.env.ref("cristo_calendar_meeting.action_calendar").id
        met_action_id = self.env.ref("cristo_calendar_meeting.action_meeting").id
        cal_menu_id = self.env.ref("cristo_calendar_meeting.calendar_main_menu").id
        met_menu_id = self.env.ref("cristo_calendar_meeting.meeting_main_menu").id
        res[0].update({'cal_action_id': cal_action_id, 'met_action_id': met_action_id,
                       'cal_menu_id': cal_menu_id,'met_menu_id':met_menu_id})

        if self.user_has_groups('cristo_calendar_meeting.group_role_enable_calendar') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            total_cal = self.env['calendar.event'].search_count([('category','=','calendar')])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_cal = self.env['calendar.event'].search_count([('category','=','calendar'),('institute_id','=',self.env.user.institute_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_cal = self.env['calendar.event'].search_count([('category','=','calendar'),('rel_province_id','=',self.env.user.rel_province_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                total_cal = self.env['calendar.event'].search_count([('category','=','calendar'),('community_id','=',self.env.user.community_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                total_cal = self.env['calendar.event'].search_count([('category','=','calendar'),('institution_id','=',self.env.user.institution_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_individual'):
                total_cal = self.env['calendar.event'].search_count([('category','=','calendar'),('partner_ids','=',self.env.user.partner_id.id)])
            res[0].update({'calendar':1,'total_cal':total_cal})
        if self.user_has_groups('cristo_calendar_meeting.group_role_enable_meeting') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            total_meet = self.env['calendar.event'].search_count([('category','=','meeting')])
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                total_meet = self.env['calendar.event'].search_count([('category','=','meeting'),('institute_id','=',self.env.user.institute_id.id),('attendee_ids.partner_id','=',self.env.user.partner_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                total_meet = self.env['calendar.event'].search_count([('category','=','meeting'),('rel_province_id','=',self.env.user.rel_province_id.id),('attendee_ids.partner_id','=',self.env.user.partner_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                total_meet = self.env['calendar.event'].search_count([('category','=','meeting'),('community_id','=',self.env.user.community_id.id),('attendee_ids.partner_id','=',self.env.user.partner_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                total_meet = self.env['calendar.event'].search_count([('category','=','meeting'),('institution_id','=',self.env.user.institution_id.id),('attendee_ids.partner_id','=',self.env.user.partner_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_individual'):
                total_cal = self.env['calendar.event'].search_count([('category','=','meeting'),('partner_ids','=',self.env.user.partner_id.id)])
            res[0].update({'meeting':1,'total_meet':total_meet})
        return res