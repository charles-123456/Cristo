# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
    cir_header_img = fields.Binary(string="Circular Header Image")
