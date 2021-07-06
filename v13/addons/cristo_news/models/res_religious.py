# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResReligiousInstitute(models.Model):
    _inherit = 'res.religious.institute'
    
    news_ids = fields.One2many('res.news', 'institute_id', string="News", copy=True)
    
class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
    news_ids = fields.One2many('res.news', 'rel_province_id', string="News", copy=True)
    
class ResReligiousCommunity(models.Model):
    _inherit = 'res.community'
    
    news_ids = fields.One2many('res.news', 'community_id', string="News", copy=True)
    