# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime
from odoo.addons.cristo.tools import cris_tools

class Collaboration(models.Model):
    _name = 'cristo.collaboration'
    _description = "Collaboration"
    _inherit = ["common.rel.fields","common.ecc.fields"]


    name = fields.Char(string="Name", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    associated_with_id = fields.Many2one('res.main.category', string="Associated With")
    state = fields.Selection([('open','Open'),('inprogress','Inprogress'),('close','Closed')], string="Status")
    co_rel_province_id = fields.Many2one('res.partner', string="Province")
    co_diocese_id =  fields.Many2one('res.partner', string="Diocese")
    co_institution_id =  fields.Many2one('res.partner', string="Institution")
    attachment_ids =  fields.Many2many('ir.attachment', string="Documents")
    mc_code = fields.Char(related='associated_with_id.code', string="Main Category Code")
    
    @api.constrains('start_date','end_date')
    def date_validation(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                cris_tools.date_validation(rec.start_date, rec.end_date)