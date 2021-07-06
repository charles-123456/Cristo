# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError

class CristoUsers(models.Model):
    _inherit = "res.users"
    
    institute_id = fields.Many2one('res.religious.institute', string="User Congregation", ondelete="restrict")
    rel_region_id = fields.Many2one('res.religious.region', string="User Religious Region", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="User Religious Province", ondelete="restrict")
    rel_zone_id = fields.Many2one('res.religious.zone', ondelete="restrict", string="User Area")   
    community_id = fields.Many2one('res.community', string="User House/Community", ondelete="restrict")
    institution_id = fields.Many2one('res.institution', string="User Institution", ondelete="restrict")
    ecc_reg_id = fields.Many2one('res.ecclesia.region',string="User Region", ondelete="restrict")
    ecc_province_id = fields.Many2one('res.ecclesia.province', string="User Province", ondelete="restrict")
    diocese_id = fields.Many2one('res.ecclesia.diocese', ondelete="restrict", string="User Diocese")
    vicariate_id = fields.Many2one('res.vicariate', ondelete="restrict", string="User Vicariate")
    parish_id = fields.Many2one('res.parish', ondelete="restrict", string="User Parish/Mission Station")
    sub_station_id = fields.Many2one('res.parish.sub.station', ondelete="restrict", string="User Sub Station")
    zone_id = fields.Many2one('res.ecclesia.zone', ondelete="restrict", string="User Zone")
    parish_bcc_id = fields.Many2one('res.parish.bcc', string='User Basic Christian Community (BCC)')
    family_id = fields.Many2one('res.family', ondelete="restrict", string="User Family")
    member_id = fields.Many2one('res.member', ondelete="restrict", string="User Member")
    association_id = fields.Many2one('res.association', ondelete="restrict", string="User Association")
    legal_entity_id = fields.Many2one('res.legal.entity', ondelete="restrict", string="User Legal Entity")
    
    
    def create(self, values):
        values['odoobot_state'] = 'disabled'
        res = super(CristoUsers, self).create(values)
        return res
    
    # Reason: when user table field values change means the ir.rule cache clear needed. Because record rule cache not cleared.  
    def write(self, values):
        res = super(CristoUsers, self).write(values)
        # clear caches linked to the users
        if self.ids:
            # DLE P139: Calling invalidate_cache on a new, well you lost everything as you wont be able to take it back from the cache
            # `test_00_equipment_multicompany_user`
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
            self.has_group.clear_cache(self)
        return res
    
    @api.onchange('institute_id','rel_province_id','community_id')
    def onchange_institute_id(self):
        if not self.institute_id:
            self.rel_province_id = self.community_id = self.institution_id = False
        if not self.rel_province_id:
            self.community_id = self.institution_id = False
        if not self.community_id:
            self.institution_id = False
        
    @api.onchange('partner_id')
    def _onchange_cristo_partner(self):
        if self.partner_id.main_category_code == 'RC':
            res = {}
            cong_member_ids = self.env['res.religious.institute'].search([('partner_id','=',self.partner_id._origin.id)]).member_ids.ids
            res['domain'] = {'member_id': [('id', 'in', cong_member_ids)]}
            return res
        if self.partner_id.main_category_code == 'RP':
            res = {}
            prov_member_ids = self.env['res.religious.province'].search([('partner_id','=',self.partner_id._origin.id)]).member_ids.ids
            res['domain'] = {'member_id': [('id', 'in', prov_member_ids)]}
            return res
        if self.partner_id.main_category_code == 'HC':
            res = {}
            com_member_ids = self.env['res.community'].search([('partner_id','=',self.partner_id._origin.id)]).member_ids.ids
            res['domain'] = {'member_id': [('id', 'in', com_member_ids)]}
            return res
        if self.partner_id.main_category_code == 'RI':
            res = {}
            inst_member_ids = self.env['res.institution'].search([('partner_id','=',self.partner_id._origin.id)]).member_ids.mapped('member_id')
            res['domain'] = {'member_id': [('id', 'in', inst_member_ids.ids)]}
            return res
        if self.partner_id.main_category_code == 'MR':
            res = {}
            member_id = self.env['res.member'].search([('partner_id','=',self.partner_id._origin.id)])
            res['domain'] = {'member_id': [('id', '=', member_id.id)]}
            return res
            
            