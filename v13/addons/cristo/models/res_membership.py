# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.addons.cristo.tools import cris_tools
from lxml import etree
import json

class Membership(models.Model):
    _name = 'res.membership'
    _description = "Membership"
    _rec_name = 'member_id'
    _sql_constraints = [
        ('member_id_uniq', 'unique (member_id)', 'The Member is unique!')
    ]
    
    @api.model
    def default_get(self, fields):
        data = super(Membership, self).default_get(fields)
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            data['membership_type'] = "RE"
        return data
    
    membership_type = fields.Selection([('LT','Lay Person'),('RE','Religious'),('SE','Secular Clergy')], string="Membership Type")
    member_id = fields.Many2one('res.member', string="Member")
    diocese_ids = fields.Many2many('res.ecclesia.diocese', string="Diocese")
    province_ids = fields.Many2many('res.religious.province', string="Province")
    association_ids = fields.Many2many('res.association', string="Association")
    status = fields.Selection([('active','Active'),('exit','Exit'),('transferred','Transferred'),('dismissed','Dismissed'),('deceased','Deceased'),('completed','Completed')], string="Status")
    membership_duration_ids = fields.One2many('res.membership.duration','life_membership_id',string="Duration")
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Membership, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            for node in doc.xpath("//field[@name='province_ids']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
class MembershipDuration(models.Model):
    _name = 'res.membership.duration'
    _description = "Membership Duration"    
    
    life_membership_id = fields.Many2one('res.membership', string="Membership")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    
    @api.constrains('date_from','date_to')
    def date_validation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                cris_tools.date_validation(rec.date_from, rec.date_to)
            