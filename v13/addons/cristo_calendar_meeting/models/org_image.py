from odoo import fields, models

class InheritOrganizationImage(models.Model):
    _inherit = 'org.image'
    
    calendar_id = fields.Many2one('calendar.event', string="Calendar") 