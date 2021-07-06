# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from odoo.addons.cristo.tools import cris_tools

class Res_Council(models.Model):
    _name = 'res.council'
    _description = "Council"
    _inherit = ["common.rel.fields", "common.ecc.fields"]
    _custom_filter_exclude_fields = ['member_ids']
    
    @api.constrains('status')
    def active_status(self):
        if self.status:
            council_id = self.env['res.council'].search_count([('status', '=', 'active')])
            if council_id > 1:
                raise ValidationError(_("Sorry! You can create only one active council."))
            
    name = fields.Char(string='Name', required=1)
    status = fields.Selection([('active', 'Active'),('archive', 'Archive')], string='Status')
    member_ids = fields.One2many('res.council.member', 'council_id', string="Members")
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)

class Council_Members(models.Model):
    _name = 'res.council.member'
    _description = "Council Members"

    member_id = fields.Many2one('res.member', string='Member', required=1)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    status = fields.Selection([('active', 'Active'),('archive', 'Archive')], string='Status')
    role_id = fields.Many2one('res.member.role', string="Role", ondelete="restrict")
    council_id = fields.Many2one('res.council', string="Member", ondelete='cascade')
    
    @api.constrains('date_from','date_to')
    def date_validation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                cris_tools.date_validation(rec.date_from, rec.date_to)
