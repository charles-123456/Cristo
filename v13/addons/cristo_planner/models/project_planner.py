# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectPlan(models.Model):
    _name = "project.plan"
    _inherit = ['project.plan','common.rel.fields']
    _custom_filter_exclude_fields = ['currency_id','section1_ids','section2_ids','section3_ids','section4_ids','attachment_id']
    
    @api.model
    def default_get(self, fields):
        data = super(ProjectPlan, self).default_get(fields)
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
            data['scope'] = 'congregation'
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            data['scope'] = 'province'
        if self.user_has_groups('cristo.group_role_cristo_religious_house'):
            data['scope'] = 'community'
        if self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            data['scope'] = 'institution'
        return data
    
    scope = fields.Selection([('congregation','Congregation'),('diocese','Diocese'),('regional','Regional'),('province','Province'),('community','Community'),('institution','Institution'),('personal','Personal')], string="Scope")
    

class PlanActivity(models.Model):
    _inherit = "plan.activity"
    
