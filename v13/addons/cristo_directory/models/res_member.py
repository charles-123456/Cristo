from odoo import fields,models,api


class ResMember(models.Model):
    _inherit = 'res.member'

    holyorder_date = fields.Date(string="Holy Order Date", compute="_compute_holyorder_date")

    @api.depends('holyorder_ids')
    def _compute_holyorder_date(self):
        self.holyorder_date = False
        for rec in self:
            for holy in rec.holyorder_ids:
                if holy.order == 'priest':
                    rec.holyorder_date = holy.date