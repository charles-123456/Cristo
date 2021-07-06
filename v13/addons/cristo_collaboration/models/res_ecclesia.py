# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class EcclesiaDiocese(models.Model):
    _inherit = 'res.ecclesia.diocese'

    collaboration_ids = fields.One2many('cristo.collaboration', 'diocese_id', string="Collaboration")
