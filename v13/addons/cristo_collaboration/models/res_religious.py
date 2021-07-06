# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

    
class ReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
    collaboration_ids = fields.One2many('cristo.collaboration', 'rel_province_id', string="Collaboration")
    
