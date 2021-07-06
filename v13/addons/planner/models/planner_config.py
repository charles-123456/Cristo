# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, Warning

class PlanCategory(models.Model):
    _name = "plan.category"
    _description = 'Plan Category'
    
    name = fields.Char(string="Category", required=True)
    
class PlanMainActivityType(models.Model):
    _name = "plan.main.activity.type"
    _description = 'Plan Activity Type'
    
    name = fields.Char(string="Activity Type", required=True)
    
class FundingSourceType(models.Model):
    _name = "fund.source.type"
    _description = 'Fund Source Type'
    
    name = fields.Char(string="Activity Type", required=True)
    
class SectionConfig(models.Model):
    _name = "plan.section.config"
    _description = 'Plan Section Config'
    
    @api.constrains('section_type','user_ids')
    def validate_section_type(self):
        for user in self.user_ids:
            section_ids = self.env['plan.section.config'].search_count([('section_type','=',self.section_type),('user_ids','=',user.id)])
            if section_ids > 1:
                raise UserError(_("Type for the user is already exists. Type is Unique for a User!"))
        
    name = fields.Char(string="Section Name", required=True)
    section_type = fields.Selection([('section 1','Section 1'),('section 2','Section 2'),('section 3','section 3'),('section 4', 'Section 4')], string="Type")
    user_ids = fields.Many2many('res.users', string="User", required=True)
       
    
       