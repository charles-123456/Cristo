# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from odoo.addons.cristo.tools import cris_tools

class ResCommission(models.Model):
    _name = 'res.commission'
    _description = "Commission"
    _inherit = ["common.rel.fields","common.ecc.fields"]
    _custom_filter_exclude_fields = ['commission_member_ids']
    
    name = fields.Char(string='Name', required=1)
    commission_member_ids = fields.One2many('res.commission.member', 'commission_id', string="Members")
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)
     
class CommissionMembers(models.Model):
    _name = 'res.commission.member'
    _description = "Commission Members"

#     member_id = fields.Many2one('res.member', string='Member', required=1)
    partner_id = fields.Many2one('res.partner', string="Member/Associate",required=True)
    role_id = fields.Many2one('res.member.role', string="Role", ondelete="restrict")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    status = fields.Selection([('active', 'Active'),('archive', 'Archive')], string='Status')
    commission_id = fields.Many2one('res.commission', string="Member", ondelete='cascade')
    
    @api.constrains('date_from','date_to')
    def date_validation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                cris_tools.date_validation(rec.date_from, rec.date_to)