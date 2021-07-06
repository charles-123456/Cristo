from odoo import models, fields, _, api

class ProvinceStatistics(models.TransientModel):
    _name = 'province.statistic.update'
    _description = 'Province Statistics'

    diocese_id = fields.Many2one('res.ecclesia.diocese', string='Diocese')
    generalate = fields.Integer(string="No. of Generalate")
    provincialate = fields.Integer(string="No. of Provincialate")
    regionalate = fields.Integer(string="No. of Regionalate")

    @api.onchange('diocese_id')
    def _onchange_diocese_id(self):
        if self.diocese_id:
            self.generalate = self.diocese_id.generalate
            self.provincialate = self.diocese_id.provincialate
            self.regionalate = self.diocese_id.regionalate

    def update_province_statistics(self):
        if self.diocese_id:
            self.diocese_id.write({'generalate': self.generalate,'provincialate': self.provincialate,'regionalate': self.regionalate})
