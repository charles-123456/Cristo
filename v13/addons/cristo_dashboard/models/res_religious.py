# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from datetime import date,datetime
from odoo.exceptions import ValidationError

class ResReligiousInstitute(models.Model):
    _inherit = 'res.religious.institute'
    
    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))
            
    org_image_ids = fields.One2many('org.image', 'institute_id', string="Media", copy=True)
    welcome_msg = fields.Char(string="Home Welcome Message")

class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))
            
    org_image_ids = fields.One2many('org.image', 'rel_province_id', string="Media", copy=True)
    welcome_msg = fields.Char(string="Home Welcome Message")
    
class ReligiousCommunity(models.Model):
    _inherit = 'res.community'
    
    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))
    
    org_image_ids = fields.One2many('org.image', 'house_id', string="Media", copy=True)
    welcome_msg = fields.Char(string="Home Welcome Message")
    
class Institution(models.Model):
    _inherit = 'res.institution'
    
    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))
    
    org_image_ids = fields.One2many('org.image', 'institution_id', string="Media", copy=True)
    welcome_msg = fields.Char(string="Home Welcome Message")
    