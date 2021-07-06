# -*- coding: utf-8 -*-
from odoo import models, api, _

class EcclesiaMember(models.Model):
    _inherit = 'res.member'

    @api.model
    def get_diocese_parish_details(self):
        res = super(EcclesiaMember, self).get_diocese_parish_details()
        if self.user_has_groups('cristo_calendar_meeting.group_role_enable_calendar') or self.user_has_groups(
                'cristo.group_role_cristo_bsa_super_admin'):
            total_cal = self.env['calendar.event'].search_count([('category', '=', 'calendar')])
            if self.user_has_groups('cristo.group_role_cristo_diocese'):
                total_cal = self.env['calendar.event'].search_count(
                    [('category', '=', 'calendar'), ('diocese_id', '=', self.env.user.diocese_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_vicarate'):
                total_cal = self.env['calendar.event'].search_count(
                    [('category', '=', 'calendar'), ('vicariate_id', '=', self.env.user.vicariate_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_parish_ms'):
                total_cal = self.env['calendar.event'].search_count(
                    [('category', '=', 'calendar'), ('parish_id', '=', self.env.user.parish_id.id)])
            res[0].update({'calendar': 1, 'total_cal': total_cal})

        if self.user_has_groups('cristo_calendar_meeting.group_role_enable_meeting') or self.user_has_groups(
                'cristo.group_role_cristo_bsa_super_admin'):
            total_meet = self.env['calendar.event'].search_count([('category', '=', 'meeting')])
            if self.user_has_groups('cristo.group_role_cristo_diocese'):
                total_meet = self.env['calendar.event'].search_count(
                    [('category', '=', 'meeting'),'|',('diocese_id', '=', self.env.user.diocese_id.id),
                     ('attendee_ids.partner_id', '=', self.env.user.partner_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_vicarate'):
                total_meet = self.env['calendar.event'].search_count(
                    [('category', '=', 'meeting'),'|', ('vicariate_id', '=', self.env.user.vicariate_id.id),
                     ('attendee_ids.partner_id', '=', self.env.user.partner_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_parish_ms'):
                total_meet = self.env['calendar.event'].search_count(
                    [('category', '=', 'meeting'),'|',('parish_id', '=', self.env.user.parish_id.id),
                     ('attendee_ids.partner_id', '=', self.env.user.partner_id.id)])
            res[0].update({'meeting': 1, 'total_meet': total_meet})
        return res