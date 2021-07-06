# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class Concern(models.Model):
    _name = 'concern.tags'
    _description = "Concern Tags"
    
    name = fields.Char(string='Name', required=True)
     
