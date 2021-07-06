# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResReligiousInstitute(models.Model):
    _inherit = 'res.religious.institute'
    
    def open_calendar(self):
        action = self.env.ref('cristo_dashboard.action_event_summary').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action

class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
     
    def open_calendar(self):
        action = self.env.ref('cristo_dashboard.action_event_summary').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_rel_province_id':%d}" % (self.id),
        })
        return action
    
    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_rel_province_id':%d}" % (self.id),
        })
        return action
    
class ReligiousCommunity(models.Model):
    _inherit = 'res.community'
     
    def open_calendar(self):
        action = self.env.ref('cristo_dashboard.action_event_summary').read()[0]
        action.update({
            'domain': [('community_id','=',self.id)],
            'context': "{'default_community_id':%d}" % (self.id),
        })
        return action
    
    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('community_id','=',self.id)],
            'context': "{'default_community_id':%d}" % (self.id),
        })
        return action
     
class Institution(models.Model):
    _inherit = 'res.institution'
     
    def open_calendar(self):
        action = self.env.ref('cristo_dashboard.action_event_summary').read()[0]
        action.update({
            'domain': [('institution_id','=',self.id)],
            'context': "{'default_institution_id':%d}" % (self.id),
        })
        return action
    
    def open_meeting(self):
        action = self.env.ref('cristo_calendar_meeting.action_meeting').read()[0]
        action.update({
            'domain': [('institution_id','=',self.id)],
            'context': "{'default_institution_id':%d}" % (self.id),
        })
        return action