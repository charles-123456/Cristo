# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MemberRole(models.Model):
    _inherit = "res.member.role"

    term = fields.Selection([('year','Year(s)')],string="Term", default='year')
    term_value = fields.Integer(string="Term Value")