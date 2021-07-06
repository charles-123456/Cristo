# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResMember(models.Model):
    _inherit = "res.member"
    
    next_transfer_date = fields.Date(string="Next Transfer Date")