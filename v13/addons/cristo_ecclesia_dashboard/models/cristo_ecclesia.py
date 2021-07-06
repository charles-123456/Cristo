from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResDiocese(models.Model):
    _inherit = 'res.ecclesia.diocese'
    
    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))
            
    org_image_ids = fields.One2many('org.image', 'diocese_id', string="Extra Org Media", copy=True)
    
class ResEcclesiaVicariate(models.Model):
    _inherit = 'res.vicariate'

    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))

    org_image_ids = fields.One2many('org.image', 'vicariate_id', string="Extra Org Media", copy=True)

class ResEcclesiaParish(models.Model):
    _inherit = 'res.parish'

    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))

    org_image_ids = fields.One2many('org.image', 'parish_id', string="Extra Org Media", copy=True)