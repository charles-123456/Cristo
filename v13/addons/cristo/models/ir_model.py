from odoo import models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def name_get(self):
        res = []
        for field in self:
            if self._context.get('show_description',False):
                res.append((field.id, '%s' % (field.field_description)))
            else:
                res.append((field.id, '%s (%s)' % (field.field_description, field.model)))
        return res