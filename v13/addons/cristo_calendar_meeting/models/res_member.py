# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = 'res.member'
    
    def open_calendar(self):
        action = self.env.ref('cristo_dashboard.action_event_summary').read()[0]
        action.update({
            'domain': [('partner_id','=',self.partner_id.id)],
#             'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('partner_id','=',self.partner_id.id)],
#             'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action