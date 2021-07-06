# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResEcclesiaDiocese(models.Model):
    _inherit = 'res.ecclesia.diocese'
    
    def _compute_check_calendar_authorize(self):
        for rec in self:
            rec.is_calendar_show = False
            if self.user_has_groups('cristo.group_role_cristo_ec_region,cristo.group_role_cristo_ec_province,cristo.group_role_cristo_diocese,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_calendar_show = True
                
    def _compute_check_meeting_authorize(self):
        for rec in self:
            rec.is_meeting_show = False
            if self.user_has_groups('cristo.group_role_cristo_ec_region,cristo.group_role_cristo_ec_province,cristo.group_role_cristo_diocese,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_meeting_show = True
    
    is_calendar_show = fields.Boolean(compute="_compute_check_calendar_authorize")
    is_meeting_show = fields.Boolean(compute="_compute_check_meeting_authorize")
    
    def open_calendar(self):
        action = self.env.ref('cristo_calendar_meeting.action_calendar').read()[0]
        action.update({
            'domain': [('diocese_id', '=', self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action

    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action

class ResEcclesiaVicariate(models.Model):
    _inherit = 'res.vicariate'
    
    def _compute_check_calendar_authorize(self):
        for rec in self:
            rec.is_calendar_show = False
            if self.user_has_groups('cristo.group_role_cristo_ec_region,cristo.group_role_cristo_ec_province,cristo.group_role_cristo_diocese,cristo.group_role_cristo_vicarate,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_calendar_show = True
                
    def _compute_check_meeting_authorize(self):
        for rec in self:
            rec.is_meeting_show = False
            if self.user_has_groups('cristo.group_role_cristo_ec_region,cristo.group_role_cristo_ec_province,cristo.group_role_cristo_diocese,cristo.group_role_cristo_vicarate,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_meeting_show = True
    
    is_calendar_show = fields.Boolean(compute="_compute_check_calendar_authorize")
    is_meeting_show = fields.Boolean(compute="_compute_check_meeting_authorize")
    
    def open_calendar(self):
        action = self.env.ref('cristo_calendar_meeting.action_calendar').read()[0]
        action.update({
            'domain': [('vicariate_id', '=', self.id)],
            'context': "{'default_diocese_id':%d,'default_vicariate_id':%d}" % (self.diocese_id.id, self.id),
        })
        return action

    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('vicariate_id', '=', self.id)],
            'context': "{'default_diocese_id':%d,'default_vicariate_id':%d}" % (self.diocese_id.id, self.id),
        })
        return action