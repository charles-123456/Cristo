# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class EcclesiaDiocese(models.Model):
    _inherit = 'res.ecclesia.diocese'
    
    def _compute_check_commission_authorize(self):
        for rec in self:
            rec.is_commission_show = False
            if self.user_has_groups('cristo.group_role_cristo_ec_region,cristo.group_role_cristo_ec_province,cristo.group_role_cristo_diocese,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_commission_show = True
    
    is_commission_show = fields.Boolean(compute="_compute_check_commission_authorize")
    
    def open_commission(self):
        action = self.env.ref('cristo_commission.action_res_commission').read()[0]
        action.update({
            'domain': [('diocese_id', '=', self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action

class EcclesiaVicariate(models.Model):
    _inherit = 'res.vicariate'
    
    def _compute_check_commission_authorize(self):
        for rec in self:
            rec.is_commission_show = False
            if self.user_has_groups('cristo.group_role_cristo_ec_region,cristo.group_role_cristo_ec_province,cristo.group_role_cristo_diocese,cristo.group_role_cristo_vicarate,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_commission_show = True
    
    is_commission_show = fields.Boolean(compute="_compute_check_commission_authorize")
    
    def open_commission(self):
        action = self.env.ref('cristo_commission.action_res_commission').read()[0]
        action.update({
            'domain': [('vicariate_id', '=', self.id)],
            'context': "{'default_diocese_id':%d,'default_vicariate_id':%d}" % (self.diocese_id.id, self.id),
        })
        return action