# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class ReligiousInstitute(models.Model):
    _inherit = 'res.religious.institute'
    
#     def _compute_check_commission_authorize(self):
#         for rec in self:
#             rec.is_commission_show = False
#             if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_commission_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') and self.env.user.institute_id.id == rec.id:
#                 rec.is_commission_show = True
#     
#     is_commission_show = fields.Boolean(compute="_compute_check_commission_authorize")
    
    def open_commission(self):
        action = self.env.ref('cristo_commission.action_res_commission').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
             })
        return action
    
class ReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
#     def _compute_check_commission_authorize(self):
#         for rec in self:
#             rec.is_commission_show = False
#             if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_commission_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_religious_province') and self.env.user.rel_province_id.id == rec.id:
#                 rec.is_commission_show = True
#     
#     is_commission_show = fields.Boolean(compute="_compute_check_commission_authorize")
    
    def open_commission(self):
        action = self.env.ref('cristo_commission.action_res_commission').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_institute_id':%d,'default_rel_province_id':%d}" % (self.institute_id.id,self.id)
             })
        return action
    
class ReligiousCommunity(models.Model):
    _inherit = 'res.community'
    
#     def _compute_check_commission_authorize(self):
#         for rec in self:
#             rec.is_commission_show = False
#             if self.user_has_groups('cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
#                 rec.is_commission_show = True
#             elif self.user_has_groups('cristo.group_role_cristo_religious_house') and self.env.user.community_id.id == rec.id:
#                 rec.is_commission_show = True
#     
#     is_commission_show = fields.Boolean(compute="_compute_check_commission_authorize")
    
    def open_commission(self):
        action = self.env.ref('cristo_commission.action_res_commission').read()[0]
        action.update({
            'domain' : [('community_id','=',self.id)],
            'context': "{'default_community_id': %d,'default_institute_id':%d,'default_rel_province_id':%d}" % (self.id,self.institute_id.id,self.rel_province_id.id)
             })
        return action 
    