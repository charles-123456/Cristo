# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class OrgImage(models.Model):
    _inherit = 'org.image' 
    
    chronicle_id = fields.Many2one('cristo.chronicle', string="Chronicle")