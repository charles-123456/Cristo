# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, Warning,UserError
import base64
from odoo.addons.website.tools import get_video_embed_code

class OrganizationImage(models.Model):
    _name = 'org.image'
    _description = "Organization Image"
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(default=10, index=True)

    image_1920 = fields.Image(required=True)
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    rel_province_id = fields.Many2one('res.religious.province',string="Religious Province")
    house_id = fields.Many2one('res.community',string="House/Community")
    institution_id = fields.Many2one('res.institution',string="Institution")
    video_url = fields.Char('Video URL',
                            help='URL of a video for showcasing your organization.')
    embed_code = fields.Char(compute="_compute_embed_code")

    can_image_1024_be_zoomed = fields.Boolean("Can Image 1024 be zoomed", compute='_compute_can_image_1024_be_zoomed', store=True)
    
    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = image.image_1920 and tools.is_image_size_above(image.image_1920, image.image_1024)
            
    @api.constrains('image_1920')
    def _validate_slider_image(self):
        for rec in self:
         binary = base64.b64decode(rec.image_1920)
         if (len(binary) /1024/ 1024) > 0.5:
            raise UserError(_("The maximum upload %s size is 500 KB.") % rec.name)
        
    @api.depends('video_url')
    def _compute_embed_code(self):
        for image in self:
            image.embed_code = get_video_embed_code(image.video_url)

    @api.constrains('video_url')
    def _check_valid_video_url(self):
        for image in self:
            if image.video_url and not image.embed_code:
                raise ValidationError(_("Provided video URL for '%s' is not valid. Please enter a valid video URL.") % image.name)

    @api.model_create_multi
    def create(self, vals_list):
#         try:
        return super(OrganizationImage, self.sudo()).create(vals_list)
#         except Exception as e:
#             raise Warning(_("{}".format(e)))

    def write(self, vals_list):
#         try:
        return super(OrganizationImage, self.sudo()).write(vals_list)
#         except Exception as e:
#             raise Warning(_("{}".format(e)))