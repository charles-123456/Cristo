from odoo import models,fields

class OrgImage(models.Model):
    _inherit='org.image'
    
    diocese_id = fields.Many2one('res.ecclesia.diocese',string="Diocese")
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate")
    parish_id = fields.Many2one('res.parish', string="Parish/Mission")