from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FamilyList(models.TransientModel):
    _name = 'family.list'
    _description = 'Family List'

    @api.onchange('all_category', 'all_zone', 'all_bcc', 'category_ids', 'zone_ids', 'bcc_ids')
    def onchange_all(self):
        if self.all_bcc:
            self.bcc_ids = self.env['res.parish.bcc'].search([])

    all_category = fields.Boolean(string="All Group", default=True)
    category_ids = fields.Many2many("res.ecclesia.zone.category", string="Group")
    all_zone = fields.Boolean(string="All Zone", default=True)
    zone_ids = fields.Many2many("res.ecclesia.zone", string="Zone")
    all_bcc = fields.Boolean(string="All BCC", default=True)
    bcc_ids = fields.Many2many("res.parish.bcc", string="BCC")
    

    def print_pdf(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['all_category', 'category_ids', 'all_zone', 'zone_ids', 'all_bcc', 'bcc_ids'])[0]
        return self.env.ref('cristo.family_list').report_action(self, data=data, config=False)
