# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResReligiousInstitute(models.Model):
    _inherit = 'res.religious.institute'
    
#     def _compute_check_planner_authorize(self):
#         for rec in self:
#             rec.is_planner_show = False
#             if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_planner_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') and self.env.user.institute_id.id == rec.id:
#                 rec.is_planner_show = True
#     
#     is_planner_show = fields.Boolean(compute="_compute_check_planner_authorize")
    
    def open_project_plan(self):
        action = self.env.ref('planner.action_project_plan').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': {'default_institute_id':self.id},
        })
        return action

class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
#     def _compute_check_planner_authorize(self):
#         for rec in self:
#             rec.is_planner_show = False
#             if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_planner_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_religious_province') and self.env.user.rel_province_id.id == rec.id:
#                 rec.is_planner_show = True
#     
#     is_planner_show = fields.Boolean(compute="_compute_check_planner_authorize")
    
    def open_project_plan(self):
        action = self.env.ref('planner.action_project_plan').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': {'default_rel_province_id':self.id},
        })
        return action
    
class ReligiousCommunity(models.Model):
    _inherit = 'res.community'
    
#     def _compute_check_planner_authorize(self):
#         for rec in self:
#             rec.is_planner_show = False
#             if self.user_has_groups('cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_planner_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_religious_house') and self.env.user.community_id.id == rec.id:
#                 rec.is_planner_show = True
#     
#     is_planner_show = fields.Boolean(compute="_compute_check_planner_authorize")
    
    def open_project_plan(self):
        action = self.env.ref('planner.action_project_plan').read()[0]
        action.update({
            'domain': [('community_id','=',self.id)],
            'context': {'default_community_id':self.id},
        })
        return action
    
class Institution(models.Model):
    _inherit = 'res.institution'
    
#     def _compute_check_planner_authorize(self):
#         for rec in self:
#             rec.is_planner_show = False
#             if self.user_has_groups('cristo.group_role_cristo_religious_house,cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_planner_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution') and self.env.user.institution_id.id == rec.id:
#                 rec.is_planner_show = True
#     
#     is_planner_show = fields.Boolean(compute="_compute_check_planner_authorize")
    
    def open_project_plan(self):
        action = self.env.ref('planner.action_project_plan').read()[0]
        action.update({
            'domain': [('institution_id','=',self.id)],
            'context': {'default_institution_id':self.id},
        })
        return action