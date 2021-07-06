# -*- coding: utf-8 -*-
from odoo import models, fields


class ResEcclesiaDiocese(models.Model):
    _inherit = 'res.ecclesia.diocese'

    news_ids = fields.One2many('res.news', 'diocese_id', string="News", copy=True)
    
class ResEcclesiaParish(models.Model):
    _inherit = 'res.parish'

    news_ids = fields.One2many('res.news', 'parish_id', string="News", copy=True)